import disnake
from disnake.ext import commands

import src.Events as Events
from src.Classes import Member
from src.Logger import *


def add_members_commands(bot: disnake.Client):
    @bot.slash_command(
        name = "изменить-очки",
        description = "Изменить количество очков пользователя."
    )
    async def change_score(
        inter: disnake.CommandInteraction,
        mem: disnake.Member = commands.Param(
            name='пользователь',
            description='Пользователь, очки которого нужно изменить.'
        ),
        score: int = commands.Param(
            name="очки",
            description="количество очков, которое нужно добавить в статистику пользователя."
        )):
        member = Member(mem)
        if score >= 0: member.change_score(score, True)
        else: member.change_score(score, False)
        await inter.send(content=f"Количество очков пользователя теперь - {member.score}", ephemeral=True)


    @bot.slash_command(
        name = "изменить-статистику",
        description = "Изменить статистику пользователя."
    )
    async def change_member_stat(
        inter: disnake.CommandInteraction,
        mem: disnake.Member = commands.Param(
            name='пользователь',
            description='Пользователь, статистику которого нужно изменить.'
        ),
        param: str = commands.Param(
            name="парамерт",
            description="что в статистике нужно изменить.",
            choices=["выполненные заказы", "курирование заказов", "заметки", "предупреждения"]
        ),
        mode: str = commands.Param(
            name="режим",
            description="удалить/добавить в статистику.",
            choices=["добавить", "удалить"]
        ),
        value: str = commands.Param(
            name="значение",
            description="Значение, которое надо добавить/удалить из статистики."
        )):
        member = Member(mem)

        if param == "выполненные заказы":
            if mode == "добавить":
                member.doneTasks.append(value)
            else:
                member.doneTasks = member.rem_from_stat(member.doneTasks, value)
        elif param == "курирование заказов":
            if mode == "добавить":
                member.curationTasks.append(value)
            else:
                member.curationTasks = member.rem_from_stat(member.curationTasks, value)
        elif param == "заметки":
            if mode == "добавить":
                member.notes.append(value)
            else:
                member.notes = member.rem_from_stat(member.notes, value)
                Logger.secret(inter, f'удалена заметка "{value}" пользователя <@{mem.id}>')
        elif param == "предупреждения":
            if mode == "добавить":
                member.warns.append(value)
            else:
                member.warns = member.rem_from_stat(member.warns, value)
                Logger.secret(inter, f'удалено предепреждение "{value}" пользователя <@{mem.id}>')

        member.update()
        await inter.send(content="**Done**", ephemeral=True)
        Logger.medium(inter, f"изменена статистика пользователя {mem.name}, параметр: {param}")


    @bot.slash_command(
        name = "сикей",
        description = "Изменить сикей пользователя."
    )
    async def member_ckey(
        inter: disnake.CommandInteraction,
        mem: disnake.Member = commands.Param(
            name='пользователь',
            description='Пользователь, которому нужно привязать ckey.'
        ),
        ckey: str = commands.Param(
            name='ckey',
            description='ckey, пользователя.'
        )):
        Member(mem).set_ckey(ckey)
        await inter.send(content="**Done**", ephemeral=True)
        Logger.medium(inter, f"задан сикей пользователя {mem.name}: {ckey}")