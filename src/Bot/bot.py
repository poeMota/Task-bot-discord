import disnake
from disnake.ext import commands
from disnake import utils

from src.Config import *
from src.Classes import Project, Task, Member, SubscribePost
from src.Tools import get_projects

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
        self.subPost: SubscribePost = None
        self._initialized = True

        add_stat_commands(self)
        add_task_commands(self)
        add_config_commands(self)
        add_members_commands(self)
        add_save_commands(self)
        add_fun_commands(self)
        add_magazine(self)
        add_events(self)


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
            await project.read_project_info()
            if project.forum == forum: 
                return project
            
        return None
    

    async def get_task_by_thread(self, thread: disnake.Thread) -> (Task | None):
        if thread is not None and isinstance(thread.parent, disnake.ForumChannel):
            project: Project = await self.get_project_by_forum(thread.parent)
            if project is not None:
                return project.get_task_by_thread(thread)
            
        return None
    # endregion