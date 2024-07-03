import asyncio
import disnake
from datetime import datetime

from src.Logger import *
from src.Config import *
import src.Classes as Classes

class Task:
    _instances = {}

    def __new__(cls, project, id=0, *args, **kwargs):
        if project.name not in cls._instances:
            cls._instances[project.name] = {}
        if id in cls._instances[project.name]:
            return cls._instances[project.name][id]
        instance = super().__new__(cls)
        cls._instances[project.name][id] = instance
        return instance


    def __init__(self, project, id, thread: disnake.Thread=None) -> None:
        if not hasattr(self, '_initialized'):
            self.project: Classes.Project = project
            self.id = id
            self.timeFormat = "%Y-%m-%d"

            # Write/Read from config
            self.score = 0
            self.name = "" if thread is None else thread.name
            self.url = "" if thread is None else thread.jump_url
            self.thread: disnake.Thread = thread
            self.brigadire: disnake.Member = None
            self.members = []
            self.startDate = datetime.now().strftime(self.timeFormat)
            self.lastSave = ""
            self._maxMembers = 0
            self.maxMembers = 0

            self.read_task()

            # Temp
            self._endingResult = {}
            self._initialized = True
            self._done = False


    def read_task(self) -> None:
        project_data = json_read("projects")

        if str(self.id) not in project_data[self.project.name]["tasks"]:
            self.write_task()
            return

        self.score, self.name, self.url, self.thread, self.brigadire, self.startDate, self.lastSave, self._maxMembers, self.maxMembers = (
            0 if "score_modifier" not in project_data[self.project.name]["tasks"][str(self.id)] 
                else project_data[self.project.name]["tasks"][str(self.id)]["score_modifier"],

            "Unknown" if "name" not in project_data[self.project.name]["tasks"][str(self.id)]
                else project_data[self.project.name]["tasks"][str(self.id)]["name"],

            "" if "url" not in project_data[self.project.name]["tasks"][str(self.id)]
                else project_data[self.project.name]["tasks"][str(self.id)]["url"],

            None if "thread" not in project_data[self.project.name]["tasks"][str(self.id)]
                else self.project.forum.get_thread(project_data[self.project.name]["tasks"][str(self.id)]["thread"]),

            None if "brigadire" not in project_data[self.project.name]["tasks"][str(self.id)]
                else self.project.bot.get_member(project_data[self.project.name]["tasks"][str(self.id)]["brigadire"]),

            "" if "start_date" not in project_data[self.project.name]["tasks"][str(self.id)]
                else project_data[self.project.name]["tasks"][str(self.id)]["start_date"],

            "" if "last_save" not in project_data[self.project.name]["tasks"][str(self.id)]
                else project_data[self.project.name]["tasks"][str(self.id)]["last_save"],

            0 if "@max_members" not in project_data[self.project.name]["tasks"][str(self.id)]
                else project_data[self.project.name]["tasks"][str(self.id)]["@max_members"],

            0 if "max_members" not in project_data[self.project.name]["tasks"][str(self.id)]
                else project_data[self.project.name]["tasks"][str(self.id)]["max_members"]
        )

        for member_id in project_data[self.project.name]["tasks"][str(self.id)]["members"]:
            member = self.project.bot.get_member(member_id)
            if member is not None:
                # Change member inTasks from url to Task class
                for url in list(member.inTasks):
                    if url == self.url:
                        member.inTasks.remove(url)
                        member.inTasks.append(self)

                self.members.append(member)


    def write_task(self) -> None:
        project_data = json_read("projects")

        members = []
        for member in self.members: members.append(member.id)

        project_data[self.project.name]["tasks"][str(self.id)] = {
            "score_modifier": self.score,
            "name": self.name,
            "url": self.url,
            "thread": self.thread.id,
            "brigadire": 0 if self.brigadire is None else self.brigadire.id,
            "members": members,
            "start_date": self.startDate,
            "last_save": self.lastSave,
            "@max_members": self._maxMembers,
            "max_members": self.maxMembers
        }
        json_write("projects", project_data)
    

    def __str__(self) -> str:
        return f"**заказ**: {self.name} #{self.id}\n**ветка**: {self.url}"


    def update(self):
        if self._maxMembers == 0:
            self.score, self.maxMembers = self.get_settings()
        self.write_task()
        Logger.debug(f"обновлён заказ {self.name}")


    def on_leave(self, member):
        if member in self.members:
            if member == self.brigadire:
                self.brigadire = None
            self.members.remove(member)
            self.update()


    def on_join(self, member):
        if member not in self.members:
            self.members.append(member)
            if len(self.members) == self.maxMembers:
                loop = asyncio.get_event_loop()
                loop.create_task(self.thread.send(content=f"**Бригада достигла максимального количества человек в {self.maxMembers}**."))
            self.update()


    def get_string(self) -> str:
        return f"{self.name} {self.url}"
    

    def info_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title=f"Заказ {self.name}",
            description=f"**дата начала:** {self.startDate}",
            color=0xf1c40f,
            type="rich"
        )
        embed.add_field(name="очков за выполнение:", value=self.score, inline=False)
        if self.lastSave != "": embed.add_field(name="последний сейв:", value=self.lastSave, inline=False)
        if self.brigadire is not None: embed.add_field(name="бригадир:", value=f"- <@{self.brigadire.member.id}>", inline=False)
        text = ""
        for member in self.members:
            text += f"- <@{member.id}>\n"
        
        embed.add_field(name=f"члены бригады: ({len(self.members)}/{self.maxMembers})", value=text, inline=False)
        return embed
    

    def get_settings(self) -> int:
        for disTag in self.thread.applied_tags:
            tag = Classes.Tag(disTag, self.project)
            if tag.tagType == Classes.TagTypes.difficult:
                return tag.scoreModifier, tag.maxMembers
            
        return 0, 1000
    

    def get_ping(self) -> str:
        text = f"<@&{self.project.waiterRole.id}>"
        for disTag in self.thread.applied_tags:
            tag = Classes.Tag(disTag, self.project)
            if tag.tagType == Classes.TagTypes.ping:
                text = f"{text} <@&{tag.ping.id}>"

        return text
    

    def get_members_ping(self) -> str:
        ret = ""
        for member in self.members:
            ret += f"<@{member.member.id}> "
        return ret
    

    def is_endingResult_filled(self):
        for member in self.members:
            if member not in self._endingResult:
                return False
        return True


    async def close(self):
        self._done = True

        # Change tags
        # FIXME: sometimes doesnt work, thx discord
        tags = self.thread.applied_tags
        await self.thread.add_tags(self.project.get_tag(Classes.TagTypes.end))
        await self.thread.remove_tags(*tags)

        await self.thread.edit(locked=True)

        for member in self._endingResult:
            member.task_end(self)
        self.project.end_task(self)

    
    def set_brigadire(self, member) -> None:
        self.brigadire = member
        self.update()
    
    
    def set_last_save(self, save):
        self.lastSave = save
        self.update()
    
    def set_max_members(self, maxMem: int):
        self._maxMembers = maxMem
        self.maxMembers = maxMem
        self.update()