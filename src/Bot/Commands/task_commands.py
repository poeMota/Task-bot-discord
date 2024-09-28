import math
import disnake
from disnake.ext import commands

from src.Classes import Member, Task
from src.Logger import *
from src.Config import *
from src.Localization import LocalizationManager
from src.HelpManager import HelpManager


loc = LocalizationManager()

def add_task_commands(bot: disnake.Client):
    helper = HelpManager()

    disabled_commands = from_toml("config", "Commands")
    if not disabled_commands: disabled_commands = {}

    async def task_member_change(
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        mode: str
    ):
        await inter.response.defer(ephemeral=True)
        if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
            task: Task = await bot.get_task_by_thread(inter.channel)
            if task is not None:
                if mode == "Add":
                    Member(member).join_task(task)
                    Logger.high(inter, loc.GetString("task-add-member-log", member_name=member.name, task_name=task.name))
                    await task.thread.send(content=loc.GetString("task-add-member-message", member_id=member.id))
                else:
                    if Member(member) in task.members:
                        Member(member).leave_task(task)
                        Logger.high(inter, loc.GetString("task-remove-member-log", member_name=member.name, task_name=task.name))
                    else:
                        await inter.edit_original_message(content=loc.GetString("task-not-in-task"))
                        return

                await inter.edit_original_message(content=loc.GetString("command-done-response"))
                return

        await inter.edit_original_message(content=loc.GetString("task-not-in-active-thread"))


    if "task-add" not in disabled_commands or disabled_commands["task-add"]:
        @bot.slash_command(
            name=loc.GetString("task-add-command-name"),
            description=loc.GetString("task-add-command-description")
        )
        async def task_add(
            inter: disnake.CommandInteraction,
            member: disnake.Member = commands.Param(
                name=loc.GetString("task-add-command-param-member-name"),
                description=loc.GetString("task-add-command-param-member-description")
            )):
            await task_member_change(inter, member, mode="Add")
        helper.AddCommand(task_add)


    if "task-remove" not in disabled_commands or disabled_commands["task-remove"]:
        @bot.slash_command(
            name=loc.GetString("task-remove-command-name"),
            description=loc.GetString("task-remove-command-description")
        )
        async def task_remove(
            inter: disnake.CommandInteraction,
            member: disnake.Member = commands.Param(
                name=loc.GetString("task-remove-command-param-member-name"),
                description=loc.GetString("task-remove-command-param-member-description")
            )):
            await task_member_change(inter, member, mode="Remove")
        helper.AddCommand(task_remove)


    if "task-close" not in disabled_commands or disabled_commands["task-close"]:
        @bot.slash_command(
            name=loc.GetString("task-close-command-name"),
            description=loc.GetString("task-close-command-description")
        )
        async def task_close(inter: disnake.CommandInteraction):
            await inter.response.defer(ephemeral=True)
            if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(inter.channel)
                if task is not None:
                    task._endingResult = {}
                    if task.brigadire is not None:
                        task._endingResult[task.brigadire] = int(task.score * from_toml("config", "Task")["brigadire_score_modifier"])

                    await inter.send(loc.GetString("task-close-command-rate-message"))
                    if task.is_endingResult_filled():
                        await task.close()

                    for i in range(math.ceil(len(task.members) / from_toml("config", "max_dropdowns_per_message"))):
                        await inter.send(view=DropDownView(task, i), ephemeral=True)
                    return

            await inter.edit_original_message(content=loc.GetString("task-not-in-active-thread"))
        helper.AddCommand(task_close)


    if "brigadire" not in disabled_commands or disabled_commands["brigadire"]:
        @bot.slash_command(
            name=loc.GetString("brigadire-command-name"),
            description=loc.GetString("brigadire-command-description")
        )
        async def brigadire(
            inter: disnake.CommandInteraction
        ):
            await inter.response.defer(ephemeral=True)
            if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(inter.channel)
                if task is not None:
                    if task.brigadire is None:
                        member = Member(inter.author)

                        if member not in task.members:
                            if len(task.members) < task.maxMembers:
                                member.join_task(task)
                            else:
                                await inter.edit_original_message(loc.GetString("brigadire-command-max-members-error-message"))
                                return

                        task.set_brigadire(member)
                        await task.thread.send(loc.GetString("brigadire-command-message", member_id=member.member.id))
                        await inter.edit_original_message(content=loc.GetString("command-done-response"))
                        Logger.high(inter, loc.GetString("brigadire-command-done-log", task_name=task.name))
                    else:
                        await inter.edit_original_message(content=loc.GetString("brigadire-command-exists-error-message"))
                    return

            await inter.edit_original_message(content=loc.GetString("task-not-in-active-thread"))
        helper.AddCommand(brigadire)


    if "ping" not in disabled_commands or disabled_commands["ping"]:
        @bot.slash_command(
            name=loc.GetString("ping-command-name"),
            description=loc.GetString("ping-command-description")
        )
        async def ping(inter: disnake.CommandInteraction):
            await inter.response.defer(ephemeral=True)
            if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(inter.channel)
                if task is not None:
                    await inter.channel.send(content=task.get_members_ping())
                    await inter.edit_original_response(content=loc.GetString("command-done-response"))
                    return

            await inter.edit_original_response(content=loc.GetString("task-not-in-active-thread"))
        helper.AddCommand(ping)


    if "last-save" not in disabled_commands or disabled_commands["last-save"]:
        @bot.slash_command(
            name=loc.GetString("last-save-command-name"),
            description=loc.GetString("last-save-command-description")
        )
        async def last_save(
            inter: disnake.CommandInteraction,
            path: str = commands.Param(
                name=loc.GetString("last-save-command-param-path-name"),
                description=loc.GetString("last-save-command-param-path-description"),
                default=None
            )):
            await inter.response.defer()
            if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(inter.channel)
                if task is not None:
                    if path is not None:
                        task.set_last_save(path)
                        Logger.low(inter, loc.GetString("last-save-command-done-log", task_name=task.name, path=path))
                    else:
                        task.set_last_save(task.lastSave)
                    await inter.edit_original_message(content=loc.GetString("last-save-command-message", last_save=task.lastSave if task.lastSave != "" else loc.GetString("task-last-save-none")))
                    return

            await inter.edit_original_message(content=loc.GetString("task-not-in-active-thread"))
        helper.AddCommand(last_save)


    if "task-info" not in disabled_commands or disabled_commands["task-info"]:
        @bot.slash_command(
            name=loc.GetString("task-info-command-name"),
            description=loc.GetString("task-info-command-description")
        )
        async def task_info(inter: disnake.CommandInteraction):
            await inter.response.defer(ephemeral=True)
            if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(inter.channel)
                if task is not None:
                    await inter.edit_original_message(embed=task.info_embed())
                    return

            await inter.edit_original_message(content=loc.GetString("task-not-in-active-thread"))
        helper.AddCommand(task_info)


    if "task-change" not in disabled_commands or disabled_commands["task-change"]:
        @bot.slash_command(
            name=loc.GetString("task-change-command-name"),
            description=loc.GetString("task-change-command-description")
        )
        async def task_change(
            inter: disnake.CommandInteraction,
            param: str = commands.Param(
                name=loc.GetString("task-change-command-param-param-name"),
                description=loc.GetString("task-change-command-param-param-description"),
                choices=[loc.GetString("task-change-command-choice-max-members")]
            ),
            value: int = commands.Param(
                name=loc.GetString("task-change-command-param-value-name"),
                description=loc.GetString("task-change-command-param-value-description")
            )):
            await inter.response.defer(ephemeral=True)
            if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
                task: Task = await bot.get_task_by_thread(inter.channel)
                if task is not None:
                    if param == loc.GetString("task-change-command-choice-max-members"):
                        task.set_max_members(value)
                        await inter.edit_original_response(content=loc.GetString("command-done-response"))
                        await task.thread.send(loc.GetString("task-change-command-max-members-message").format(value=value))
                        Logger.high(inter, loc.GetString("task-change-command-max-members-log", task_name=task.name, value=value))
                        return

            await inter.edit_original_message(content=loc.GetString("task-not-in-active-thread"))
        helper.AddCommand(task_change)


# region Task End
class EndTaskDropdown(disnake.ui.StringSelect):
    def __init__(self, task: Task, member: disnake.Member, page: int):
        self.task = task
        self.member = member
        self.page = page

        options = [
            disnake.SelectOption(
                label=f"{loc.GetString(label)} (x{factor})",
                description=member.display_name,
                value=str(factor)
                )
        for label, factor in from_toml("config", "TaskEndRating").items()]

        super().__init__(
            placeholder=f"Оцените работу {member.display_name} в таске.",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        if not self.task._done:
            self.task._endingResult[Member(self.member)] = int(self.task.score * float(self.values[0]))
            await inter.send(content=f"<@{self.member.id}> получит **{int(self.task.score * float(self.values[0]))}** очков", ephemeral=True)
            if self.task.is_endingResult_filled():
                await self.task.close()
                Logger.high(inter, loc.GetString("task-close-command-done-log", task_name=self.task.name))


class DropDownView(disnake.ui.View):
    def __init__(self, task: Task, page: int):
        super().__init__()
        maxPage = from_toml("config", "max_dropdowns_per_message") # Max members on page
        for member in task.members[page * maxPage: page * maxPage + maxPage]:
            if member != task.brigadire: self.add_item(EndTaskDropdown(task, member.member, page))
# endregion

