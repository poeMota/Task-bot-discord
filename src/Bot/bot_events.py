import asyncio
import disnake
from disnake import utils

from src.Logger import *
from src.Tools import get_projects
import src.Events as Events
from src.Config import *
from src.Classes import Member, Task, Project, SubscribePost


def add_events(bot: disnake.Client):
    @bot.event
    async def on_ready():
        [Project(bot, name) for name in get_projects()]
        Logger.logChannel = await bot.fetch_channel(from_toml("config", "log"))

        subChannel: disnake.TextChannel = await bot.fetch_channel(from_toml("config", "subscribe_channel"))
        try:
            subPost: disnake.Message = await subChannel.fetch_message(from_toml("config", "subscribe_post"))
        except disnake.NotFound:
            cfg = toml_read("config")
            subPost = await subChannel.send(content="Wait...")
            cfg["subscribe_post"] = subPost.id
            toml_write("config", cfg)

        bot.subPost = SubscribePost(bot, subPost)
        bot.subPost.update()

        print(f'Logged in as {bot.user}')


    @bot.event
    async def on_member_join(member):
        guild = bot.guild()
        role = utils.get(guild.roles, id=from_toml("config", "guest_role"))
        await member.add_roles(role)


    @bot.event
    async def on_raw_reaction_add(payload: disnake.RawReactionActionEvent):
        if payload.member.bot: return
        guild: disnake.Guild = bot.guild()
        if guild is None: return
        thread: disnake.Thread = guild.get_thread(payload.channel_id)

        # Tasks join
        if (thread is not None 
            and await bot.get_project_by_forum(thread.parent) is not None
            and payload.emoji == thread.parent.default_reaction):

            task: Task = await bot.get_task_by_thread(thread)
            member = Member(payload.member)
            if task is not None and member not in task.members:
                if (len(member.inTasks) < task.project.maxBrigPerUser
                    and len(task.members) < task.maxMembers):
                    if task not in member.inTasks and task.url not in member.inTasks:
                        member.join_task(task)
                        await thread.send(content=f"<@{payload.member.id}> присоединился в бригаду.")
                else:
                    channel = bot.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)
            
        # Role post
        sub_channel = utils.get(guild.channels, id=from_toml("config", "subscribe_channel"))
        sub_post = SubscribePost(bot, await sub_channel.fetch_message(from_toml("config", "subscribe_post")))

        if payload.channel_id == sub_channel.id and payload.message_id == sub_post.id:
            if str(payload.emoji) in sub_post.givenRoles:
                member = utils.get(guild.members, id=payload.user_id)
                await member.add_roles(sub_post.givenRoles[str(payload.emoji)][0])
                Logger.debug(f"{member.display_name} получил роль {sub_post.givenRoles[str(payload.emoji)][0].name}")


    @bot.event
    async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent):
        # Role post
        guild: disnake.Guild = bot.guild()
        sub_channel = utils.get(guild.channels, id=from_toml("config", "subscribe_channel"))
        sub_post = SubscribePost(bot, await sub_channel.fetch_message(from_toml("config", "subscribe_post")))

        if payload.channel_id == sub_channel.id and payload.message_id == sub_post.id:
            if str(payload.emoji) in sub_post.givenRoles:
                member = utils.get(guild.members, id=payload.user_id)
                if member.bot: return
                await member.remove_roles(sub_post.givenRoles[str(payload.emoji)][0])
                Logger.debug(f"{member.display_name} лишился роли {sub_post.givenRoles[str(payload.emoji)][0].name}")


    @bot.event
    async def on_thread_create(thread: disnake.Thread):
        if isinstance(thread.parent, disnake.ForumChannel):
            project: Project = await bot.get_project_by_forum(thread.parent)
            if project is not None:
                # Create task
                task = Task(project, project.lastTaskId + 1, thread)
                await project.create_task(task)

                # Send ping message
                while True:
                    try:
                        await asyncio.sleep(1)
                        await task.thread.send(content=task.get_ping())
                        break
                    except: pass


    @bot.event
    async def on_thread_update(before: disnake.Thread, after: disnake.Thread):
        if before.applied_tags != after.applied_tags:
            if isinstance(after.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(after)
                if task is not None: 
                    task.update()


    @bot.event
    async def on_member_update(before: disnake.Member, after: disnake.Member):
        _roles = []
        for role in after.roles:
            if role not in before.roles:
                _roles.append(role)
        
        for projectName in get_projects():
            project = Project(bot, projectName)
            for role in _roles:
                if role in project.associatedRoles:
                    Events.onMemberInfoChanged.raiseEvent(Member(after))
                    return