import asyncio
import disnake
from disnake import guild, utils

from src.Logger import *
from src.Tools import get_projects
import src.Events as Events
from src.Config import *
from src.Classes import Member, Task, Project, SubscribePost


def add_events(bot: disnake.Client):
    @bot.event
    async def on_ready():
        [Project(bot, name) for name in get_projects()]
        guild: disnake.Guild = bot.guild()

        config = toml_read("config")
        if "log" in config:
            Logger.logChannel = await bot.fetch_channel(config["log"])
        if "notify_log_thread" in config:
            Logger.secretLogThread = utils.get(guild.threads, id=config["notify_log_thread"])

        for url in json_read("subscribe_post"):
            try:
                message = await bot.get_message_by_link(url)
                bot.subPosts[url] = SubscribePost(bot, message)
            except Exception as e:
                Logger.error(f"Ошибка при попытке найти пост выдачи ролей по ссылке {url} - {repr(e)}")

        Logger.debug("Бот запущен")


    @bot.event
    async def on_member_join(member):
        guild: disnake.Guild = bot.guild()
        config = toml_read("config")
        if "guest_role" in config:
            role = utils.get(guild.roles, id=config["guest_role"])
            await member.add_roles(role)


    @bot.event
    async def on_member_remove(mem: disnake.Member):
        for projectName in get_projects():
            project = Project(bot, projectName)
            member = Member(mem)
            if project.member_in_project(member):
                for task in project.tasks.values():
                    member.leave_task(task)


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
            if task and member not in task.members:
                if (member.in_tasks(task.project) < task.project.maxBrigPerUser
                    and len(task.members) < task.maxMembers
                    and task.project.member_in_project(member)):
                    if task not in member.inTasks and task.url not in member.inTasks:
                        member.join_task(task)
                        await thread.send(content=f"<@{payload.member.id}> присоединился в бригаду.")
                else:
                    channel = bot.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)

        # Role post
        channel = utils.get(guild.channels, id=payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.jump_url in json_read("subscribe_post"):
            sub_post = SubscribePost(bot, message)

            if str(payload.emoji) in sub_post.givenRoles:
                member = utils.get(guild.members, id=payload.user_id)
                await member.add_roles(sub_post.givenRoles[str(payload.emoji)][0])
                Logger.debug(f"{member.display_name} получил роль {sub_post.givenRoles[str(payload.emoji)][0].name}")


    @bot.event
    async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent):
        # Role post
        guild: disnake.Guild = bot.guild()
        channel = utils.get(guild.channels, id=payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.jump_url in json_read("subscribe_post"):
            sub_post = SubscribePost(bot, message)

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
                ping_msg = task.get_ping()
                if ping_msg:
                    while True:
                        try:
                            await asyncio.sleep(1)
                            await task.thread.send(content=ping_msg)
                            break
                        except: pass


    @bot.event
    async def on_thread_update(before: disnake.Thread, after: disnake.Thread):
        if before.applied_tags != after.applied_tags:
            if isinstance(after.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(after)
                if task: task.update()


    @bot.event
    async def on_member_update(before: disnake.Member, after: disnake.Member):
        if before.roles == after.roles:
            return

        added = []
        removed = []
        for role in after.roles:
            if role not in before.roles:
                added.append(role)

        for role in before.roles:
            if role not in after.roles:
                removed.append(role)

        member = Member(after)
        for projectName in get_projects():
            project = Project(bot, projectName)
            in_project = project.member_in_project(member)

            for role in added + removed:
                if role in removed and role in project.associatedRoles and not in_project:
                    for task in project.tasks.values():
                        member.leave_task(task)

                if role in project.associatedRoles:
                    Events.onMemberInfoChanged.raiseEvent(member)
                    return

