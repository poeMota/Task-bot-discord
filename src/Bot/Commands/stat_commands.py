import disnake
from disnake.ext import commands
from datetime import datetime

from src.Classes import Member
from src.Logger import *


def add_stat_commands(bot: disnake.Client):
    @bot.slash_command(
        name = "моя-статистика",
        description = "статистика пользователя."
    )
    async def my_statistis(inter: disnake.CommandInteraction):
        await inter.send(embed=Member(inter.author).stat_embed(showHidden=False), ephemeral=True)
        Logger.low(inter, "просмотрена статистика")


    @bot.slash_command(
        name = "статистика",
        description = "статистика пользователя."
    )
    async def member_statistis(
        inter: disnake.CommandInteraction,
        disMember: disnake.Member = commands.Param(
            name="пользователь",
            description="пользователь, статистику которого нужно получить."
        )):
        await inter.send(embed=Member(disMember).stat_embed(showHidden=True), ephemeral=True)
        Logger.medium(inter, "просмотрена статистика в режиме модератора")
    

    @bot.slash_command(
        name = "предупреждение",
        description = "выдать пользователю предупреждение за нарушение правил."
    )
    async def warning(
        inter: disnake.CommandInteraction,
        _member: disnake.Member = commands.Param(
            name="пользователь",
            description="пользователь, которому нужно выдать предупреждение"
        ),
        rule: str = commands.Param(
            name="правило",
            description="номер правила, который нарушил пользователь."
        ),
        text: str = commands.Param(
            name="нарушение",
            description="текст нарушения."
        )):
        await inter.response.defer(ephemeral=True)
        member = Member(_member)
        member.warns.append(f"<@{inter.author.id}> ({datetime.now().strftime("%Y-%m-%d")}): **П.{rule}**. **{text}**")
        member.update()

        await inter.edit_original_message(content="**Done**")
        Logger.high(inter, f'выдано предупреждение "**{text}**" по правилу **{rule}** для пользователя **{_member.name}**')
    

    @bot.slash_command(
        name = "заметка",
        description = "выдать пользователю заметку."
    )
    async def note(
        inter: disnake.CommandInteraction,
        _member: disnake.Member = commands.Param(
            name="пользователь",
            description="пользователь, которому нужно выдать заметку"
        ),
        text: str = commands.Param(
            name="заметка",
            description="текст заметки."
        )):
        await inter.response.defer(ephemeral=True)
        member = Member(_member)
        member.notes.append(f"<@{inter.author.id}> ({datetime.now().strftime("%Y-%m-%d")}): **{text}**")
        member.update()

        await inter.edit_original_message(content="**Done**")
        Logger.high(inter, f'выдана заметка "**{text}**" для пользователя **{_member.name}**')