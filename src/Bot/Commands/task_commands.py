import enum
import math
import disnake
from disnake.ext import commands

import src.Events as Events
from src.Classes import Member, Task
from src.Logger import *


def add_task_commands(bot: disnake.Client):
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
                    Logger.high(inter, f"добавлен пользователь {member.name} в заказ {task.name}")
                    await task.thread.send(content=f"<@{member.id}> присоединился в бригаду.")
                else:
                    if Member(member) in task.members:
                        Member(member).leave_task(task)
                        Logger.high(inter, f"удалён пользователь {member.name} из заказа {task.name}")
                    else:
                        await inter.edit_original_message(content="Пользователь не состоит в данном заказе.")
                        return

                await inter.edit_original_message(content="**Done**")
                return

        await inter.edit_original_message(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")


    @bot.slash_command(
        name="добавить-в-бригаду",
        description="Добавить пользователя в бригаду."
    )
    async def add_to_task(
        inter: disnake.CommandInteraction,
        member: disnake.Member = commands.Param(
            name="пользователь",
            description="пользователь, которого нужно добавить в бригаду."
        )):
        await task_member_change(inter, member, mode="Add")


    @bot.slash_command(
        name="удалить-из-бригады",
        description="Удалить пользователя из бригады."
    )
    async def remove_from_task(
        inter: disnake.CommandInteraction,
        member: disnake.Member = commands.Param(
            name="пользователь",
            description="пользователь, которого нужно удалить из бригады."
        )):
        await task_member_change(inter, member, mode="Remove")


    @bot.slash_command(
        name="закрыть",
        description="Закрыть заказ."
    )
    async def end_task(inter: disnake.CommandInteraction):
        await inter.response.defer(ephemeral=True)
        if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
            task: Task = await bot.get_task_by_thread(inter.channel)
            if task is not None:
                task._endingResult = {}
                if task.brigadire is not None: 
                    task._endingResult[task.brigadire] = int(task.score * 2) # TODO: move this to config
                for i in range(math.ceil(len(task.members) / maxPage)):
                    await inter.send(view=DropDownView(task, i), ephemeral=True)
                await inter.edit_original_message(f"Оцените работу участников таска:")
                Logger.high(inter, f"закрыт заказ {task.name}")
                return
        
        await inter.edit_original_message(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")


    @bot.slash_command(
        name="взять-заказ",
        description="Стать бригадиром заказа."
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
                    task.set_brigadire(member)
                    await task.thread.send(f"<@{member.member.id}> стал бригадиром заказа.")
                    await inter.edit_original_message(content="**Done**")
                    Logger.high(inter, f"стал бригадиром заказа {task.name}")
                else:
                    await inter.edit_original_message(content="У заказа уже есть бригадир!")
                return

        await inter.edit_original_message(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")


    @bot.slash_command(
        name="пинг",
        description="Пингануть всех членов бригады."
    )
    async def ping(inter: disnake.CommandInteraction):
        await inter.response.defer(ephemeral=True)
        if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
            task: Task = await bot.get_task_by_thread(inter.channel)
            if task is not None:
                await inter.channel.send(content=task.get_members_ping())
                await inter.edit_original_response(content="**Done**")
                return

        await inter.edit_original_response(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")

    
    @bot.slash_command(
        name="последний-сейв",
        description="Узнать или изменить последний сейв таска."
    )
    async def last_save(
        inter: disnake.CommandInteraction,
        path: str = commands.Param(
            name="путь",
            description="последний путь таска.",
            default=None
        )):
        await inter.response.defer()
        if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
            task: Task = await bot.get_task_by_thread(inter.channel)
            if task is not None:
                if path is not None:
                    task.set_last_save(path)
                    Logger.low(inter, f"последний сейв заказа {task.name} - {path}")
                else:
                    task.set_last_save(task.lastSave)
                await inter.edit_original_message(content=f"**Последний сейв**: {task.lastSave}")
                return
        
        await inter.edit_original_message(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")


    @bot.slash_command(
        name="таск-инфо",
        description="Узнать информацию о таске."
    )
    async def task_info(inter: disnake.CommandInteraction):
        await inter.response.defer(ephemeral=True)
        if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
            task: Task = await bot.get_task_by_thread(inter.channel)
            if task is not None:
                await inter.edit_original_message(embed=task.info_embed())
                return
        
        await inter.edit_original_message(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")


    @bot.slash_command(
        name="изменить-таск",
        description="Изменить параметры таска."
    )
    async def task_change(
        inter: disnake.CommandInteraction,
        param: str = commands.Param(
            name="параметр",
            choices=["макс. участников"]
        ),
        value: int = commands.Param(
            name="значение",
            description="новое значение параметра"
        )):
        await inter.response.defer(ephemeral=True)
        if isinstance(inter.channel, disnake.Thread) and isinstance(inter.channel.parent, disnake.ForumChannel):
            task: Task = await bot.get_task_by_thread(inter.channel)
            if task is not None:
                if param == "макс. участников":
                    task.set_max_members(value)
                    await inter.edit_original_response(content="**Done**")
                    await task.thread.send(f"максимальное количество участников таска теперь **{value}**")
                    Logger.high(inter, f"максимальное количество участников таска {task.name} теперь {value}")
                    return
        
        await inter.edit_original_message(content="Вы не находитесь в ветке активного заказа для выполения данной команды.")

# region Task End
maxPage = 6 # Max members on page


class TaskWorksTypes(enum.Enum): # TODO: move this to config
    veryGood = ["Отлично работал", "2"]
    good = ["Хорошо работал", "1.5"]
    normal = ["Работал", "1"]
    bad = ["Плохо работал", "0.5"]
    haveNoTime = ["Не успел поработать", "0"]
    noWorking = ["Не работал", "-0.5"]


class EndTaskDropdown(disnake.ui.StringSelect):
    def __init__(self, task: Task, member: disnake.Member, page: int):
        self.task = task
        self.member = member
        self.page = page
        options = [
            disnake.SelectOption(
                label=f"{TaskWorksTypes.veryGood.value[0]} (x{TaskWorksTypes.veryGood.value[1]})", 
                description=member.display_name,
                value=TaskWorksTypes.veryGood.value[1]
                ),
            disnake.SelectOption(
                label=f"{TaskWorksTypes.good.value[0]} (x{TaskWorksTypes.good.value[1]})",
                description=member.display_name,
                value=TaskWorksTypes.good.value[1]
                ),
            disnake.SelectOption(
                label=f"{TaskWorksTypes.normal.value[0]} (x{TaskWorksTypes.normal.value[1]})",
                description=member.display_name,
                value=TaskWorksTypes.normal.value[1]
                ),
            disnake.SelectOption(
                label=f"{TaskWorksTypes.bad.value[0]} (x{TaskWorksTypes.bad.value[1]})",
                description=member.display_name,
                value=TaskWorksTypes.bad.value[1]
                ),
            disnake.SelectOption(
                label=f"{TaskWorksTypes.haveNoTime.value[0]} (x{TaskWorksTypes.haveNoTime.value[1]})",
                description=member.display_name,
                value=TaskWorksTypes.haveNoTime.value[1]
                ),
            disnake.SelectOption(
                label=f"{TaskWorksTypes.noWorking.value[0]} (x{TaskWorksTypes.noWorking.value[1]})",
                description=member.display_name,
                value=TaskWorksTypes.noWorking.value[1]
                )
        ]

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
                await inter.send(content="Заказ завершен :white_check_mark:")


class DropDownView(disnake.ui.View):
    def __init__(self, task: Task, page: int):
        super().__init__()
        for member in task.members[page * maxPage: page * maxPage + maxPage]:
            if member != task.brigadire: self.add_item(EndTaskDropdown(task, member.member, page))
# endregion