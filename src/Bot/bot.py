import disnake
from disnake.ext import commands
from disnake import utils

from src.Logger import *
from src.Config import *
from src.Classes import Project, Task, Member, SubscribePost
from src.Tools import get_projects
from src.Localization import LocalizationManager

from src.Bot.Commands import *
from src.Bot.Magazine import add_magazine
from src.Bot.bot_events import add_events


class Bot(commands.InteractionBot):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(Bot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        super().__init__(intents=disnake.Intents.all(), test_guilds=[from_toml("config", "guild")])
        self.subPosts: dict[SubscribePost] = {}
        self._initialized = True

        add_stat_commands(self)
        add_task_commands(self)
        add_config_commands(self)
        add_members_commands(self)
        add_save_commands(self)
        add_fun_commands(self)
        add_magazine(self)
        add_help_commands(self)
        add_events(self)

        LocalizationManager()


    # region Tools

    def guild(self) -> disnake.Guild:
        guild_id = from_toml("config", "guild")
        guild = self.get_guild(guild_id)

        if guild is not None: return guild
        else: raise ValueError("No guild found for bot.")


    def get_role(self, role_id: int) -> disnake.Role:
        guild = self.guild()
        return utils.get(guild.roles, id=role_id)


    def get_member(self, user_id) -> disnake.Member:
        guild = self.guild()
        disMember = utils.get(guild.members, id=user_id)
        return None if disMember is None else Member(disMember)


    async def get_project_by_forum(self, forum: disnake.ForumChannel) -> (Project | None):
        for name in get_projects():
            project = Project(self, name)
            if project.forum == forum:
                return project

        return None


    async def get_task_by_thread(self, thread: disnake.Thread) -> (Task | None):
        if thread is not None and isinstance(thread.parent, disnake.ForumChannel):
            project: Project = await self.get_project_by_forum(thread.parent)
            if project is not None:
                return project.get_task_by_thread(thread)

        return None


    async def restart(self):
        Logger.debug(f"перезапуск бота...")
        for name in get_projects():
            try:
                project = Project(self, name)
                await project.read_project_info()
                Logger.debug(f"обновлён проект {name}")
                for task in project.tasks:
                    try:
                        if isinstance(task, Task):
                            task.read_task()
                            Logger.debug(f"обновлён заказ {task.name}")
                    except Exception as e:
                        Logger.debug(f"Ошибка при обновлении заказа {task.name} - {repr(e)}, завершаем перезапуск")
                        return
            except Exception as e:
                Logger.debug(f"ошибка при обновлении проекта {name} - {repr(e)}, завершаем перезапуск")
                return

        loc = LocalizationManager()
        loc.CollectLocale()
        Logger.debug("локализация перезагружена")
        Logger.debug("бот успешно перезапущен")


    def parse_message_link(self, link: str):
        try:
            parts = link.split("/")
            guild_id = int(parts[-3])
            channel_id = int(parts[-2])
            message_id = int(parts[-1])
            return guild_id, channel_id, message_id
        except (ValueError, IndexError):
            return None, None, None


    async def get_message_by_link(self, link: str) -> disnake.Message:
        _, channel_id, message_id = self.parse_message_link(link)
        guild = self.guild()

        if not (guild and channel_id and message_id):
            raise ValueError("Wrong message url")

        channel = await guild.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        return message
    # endregion

