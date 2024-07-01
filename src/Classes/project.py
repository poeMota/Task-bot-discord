import asyncio
import disnake

import src.Classes as Classes
from src.EventManager import Event
from src.Config import *
from src.Tools import *
from src.Logger import *

import src.Events as Events


class Project:
    _instances = {}

    def __new__(cls, bot, name, *args, **kwargs):
        if name in cls._instances:
            return cls._instances[name]
        instance = super().__new__(cls)
        cls._instances[name] = instance
        return instance


    def __init__(self, bot: disnake.Client, name) -> None:
        if not hasattr(self, '_initialized'):
            self.bot = bot
            self.inited = False
            
            # Write/Read from config
            self.name = name
            self.lastTaskId = 0
            self.maxBrigPerUser = 0
            self.forum: disnake.ForumChannel = 0
            self.waiterRole: disnake.Role = 0
            self.mainChannel: disnake.TextChannel = 0
            self.statPost: disnake.Message = {}
            self.statChannel: disnake.TextChannel = 0
            self.associatedRoles = []
            self.tags = []
            self.tasks = {}

            loop = asyncio.get_event_loop()
            loop.create_task(self.read_project_info())


            # Subscribes
            Events.onProjectInfoChanged.subscribe(self.update)
            Events.onProjectInfoChanged.subscribe(self.update_stat_post)
            Events.onMemberInfoChanged.subscribe(self.update_stat_post)

            Events.onTagCreate.subscribe(self.on_tag_create)

            self._initialized = True

    
    def __repr__(self) -> str:
        return f"project {self.name}"


    async def read_project_info(self) -> None:
        project_data = json_read("projects")

        if self.name not in project_data:
            self.write_project_info()
            return

        self.maxBrigPerUser, self.lastTaskId, self.forum, self.waiterRole, self.mainChannel, self.statChannel = (
            project_data[self.name]["max_brigades_per_user"],
            project_data[self.name]["last_task_id"],
            self.bot.get_channel(project_data[self.name]["forum"]),
            self.bot.get_role(project_data[self.name]["waiter_role"]),
            self.bot.get_channel(project_data[self.name]["main_channel"]),
            self.bot.get_channel(project_data[self.name]["stat_channel"])
        )

        for tag_id in project_data[self.name]["tags"]:
            tag = Classes.Tag(self.forum.get_tag(int(tag_id)), self)
            if tag not in self.tags: self.tags.append(tag)

        for task_id in project_data[self.name]["tasks"]:
            self.tasks[int(task_id)] = Classes.Task(self, int(task_id))

        for role_id in project_data[self.name]["associated_roles"]:
            role = self.bot.get_role(role_id)
            if role not in self.associatedRoles: self.associatedRoles.append(role)


        try:
            for role_id in project_data[self.name]["stat_post"]:
                self.statPost[self.bot.get_role(int(role_id))] = await self.bot.get_channel(
                    project_data[self.name]["stat_channel"]
                    ).fetch_message(
                        project_data[self.name]["stat_post"][role_id]
                        )
        except Exception as e:
            print(repr(e))
            Logger.debug(f"Ошибка при чтении поста статистики {self.name}, {repr(e)}, создаём новый")
            await self.send_stat_post()
        
        self.inited = True


    def write_project_info(self):
        _stat_posts = {}
        for role in self.statPost:
            _stat_posts[role.id] = self.statPost[role].id

        project_data = json_read("projects")

        project_data[self.name] = {
            "max_brigades_per_user": self.maxBrigPerUser,
            "last_task_id": self.lastTaskId,
            "forum": self.forum.id,
            "waiter_role": self.waiterRole.id,
            "main_channel": self.mainChannel.id,
            "stat_post": _stat_posts,
            "stat_channel": self.statChannel.id,
            "associated_roles": [role.id for role in self.associatedRoles],
            "tags": {},
            "tasks": {}
        }

        json_write("projects", project_data)

        for tag in self.tags:
            tag.write_tag()

        for task_id in self.tasks:
            self.tasks[task_id].write_task()


    def update(self, ev: Event):
        if ev.Raiser == self:
            self.write_project_info()


    def on_tag_create(self, ev: Event):
        if ev.Raiser.project == self:
            self.tags.append(ev.Raiser)
            self.write_project_info()
    

    def delete_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.write_project_info()


    def get_task_by_thread(self, thread: disnake.Thread):
        for task in self.tasks.values():
            if thread == task.thread:
                return task
        return None
    

    def get_task_by_url(self, url: str):
        for task in self.tasks.values():
            if url == task.url:
                return task
        return None


    def get_tag(self, type):
        for tag in self.tags:
            if tag.tagType == type:
                return tag.tag
        return None


    async def create_task(self, task):
        self.lastTaskId += 1
        self.tasks[task.id] = task
        task.score, task.maxMembers = task.get_settings()

        inWorkTag = self.get_tag(Classes.TagTypes.inWork)
        if inWorkTag is not None: 
            try:
                await task.thread.add_tags(inWorkTag)
            except Exception as e:
                print(repr(e))
                Logger.debug(f"ошибка при попытке добавить тег к таску {task.name}: {repr(e)}")

        self.write_project_info()
        Logger.debug(f"создан заказ {task.name} для проекта {self.name}")


    def end_task(self, task):
        del self.tasks[task.id]
        self.write_project_info()
    

    def config_embed(self):
        return embed_from_dict(
        title=f"Проект {self.name}",
        description=f"конфиг проекта",
        color=disnake.Colour.light_gray(),
        D={
            "макс. бригад для человека": self.maxBrigPerUser,
            "роль ждуна": f"<@&{self.waiterRole.id}>",
            "форум": f"<#{self.forum.id}>",
            "основной канал": f"<#{self.mainChannel.id}>",
            "канал статистики": f"<#{self.statChannel.id}>",
            "роли проекта": [f"<@&{role.id}>" for role in self.associatedRoles],
            "теги": [str(tag) for tag in self.tags],
            "таски": [str(task) for task in self.tasks]
        },
        showHidden=True)


    def project_stat_embed(self):
        embeds = {}
        for role in self.associatedRoles:
            embed = Embed(
                title=f"{role.name} ({len(role.members)})",
                description="ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ",
                color=role.color,
                type="rich"
            )
            embeds[role] = embed

        guild: disnake.Guild = self.bot.guild()
        for disMember in guild.members:
            last_role = None
            for role in disMember.roles:
                if role in self.associatedRoles:
                    last_role = role
            if last_role is not None:
                member = Classes.Member(disMember)
                embeds[last_role].add_field(name=disMember.name, value=member.stat_post_text())

        return embeds
    

    async def send_stat_post(self):
        embeds = self.project_stat_embed()
        
        for role in embeds:
            self.statPost[role] = await self.statChannel.send(embed=embeds[role])

        self.write_project_info()

    def update_stat_post(self, ev: Event):
        if self.inited:
            loop = asyncio.get_event_loop()
            embeds = self.project_stat_embed()
            for role in self.associatedRoles:
                loop.create_task(
                    self.statPost[role].edit(embed=embeds[role])
                    )
            Logger.debug(f"обновлен пост статистики проекта {self.name}")


    def __del__(self):
        self.write_project_info()