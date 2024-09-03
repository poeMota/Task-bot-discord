import disnake
from disnake.ext import commands
from datetime import datetime

from src.Classes import Member
from src.Logger import *
from src.Localization import LocalizationManager


def add_stat_commands(bot: disnake.Client):
    loc = LocalizationManager()

    @bot.slash_command(
        name=loc.GetString("my-statistics-command-name"),
        description=loc.GetString("my-statistics-command-description")
    )
    async def my_statistics(inter: disnake.CommandInteraction):
        await inter.send(embed=Member(inter.author).stat_embed(showHidden=False), ephemeral=True)
        Logger.low(inter, loc.GetString("my-statistics-command-log-viewed"))


    @bot.slash_command(
        name=loc.GetString("member-statistics-command-name"),
        description=loc.GetString("member-statistics-command-description")
    )
    async def member_statistics(
        inter: disnake.CommandInteraction,
        disMember: disnake.Member = commands.Param(
            name=loc.GetString("member-statistics-command-param-user-name"),
            description=loc.GetString("member-statistics-command-param-user-description")
        )):
        await inter.send(embed=Member(disMember).stat_embed(showHidden=True), ephemeral=True)
        Logger.medium(inter, loc.GetString("member-statistics-command-log-viewed", username=disMember.name))


    @bot.slash_command(
        name=loc.GetString("warning-command-name"),
        description=loc.GetString("warning-command-description")
    )
    async def warning(
        inter: disnake.CommandInteraction,
        _member: disnake.Member = commands.Param(
            name=loc.GetString("warning-command-param-user-name"),
            description=loc.GetString("warning-command-param-user-description")
        ),
        rule: str = commands.Param(
            name=loc.GetString("warning-command-param-rule-name"),
            description=loc.GetString("warning-command-param-rule-description")
        ),
        text: str = commands.Param(
            name=loc.GetString("warning-command-param-violation-name"),
            description=loc.GetString("warning-command-param-violation-description")
        )):
        await inter.response.defer(ephemeral=True)
        member = Member(_member)
        member.warns.append(f"<@{inter.author.id}> ({datetime.now().strftime('%Y-%m-%d')}): **П.{rule}**. **{text}**")
        member.update()

        await inter.edit_original_message(content=loc.GetString("command-done-response"))
        _text = loc.GetString("warning-command-log-issued", text=text, rule=rule, username=_member.name)
        Logger.high(inter, _text)
        Logger.secret(inter, _text)


    @bot.slash_command(
        name=loc.GetString("note-command-name"),
        description=loc.GetString("note-command-description")
    )
    async def note(
        inter: disnake.CommandInteraction,
        _member: disnake.Member = commands.Param(
            name=loc.GetString("note-command-param-user-name"),
            description=loc.GetString("note-command-param-user-description")
        ),
        text: str = commands.Param(
            name=loc.GetString("note-command-param-note-name"),
            description=loc.GetString("note-command-param-note-description")
        )):
        await inter.response.defer(ephemeral=True)
        member = Member(_member)
        member.notes.append(f"<@{inter.author.id}> ({datetime.now().strftime('%Y-%m-%d')}): **{text}**")
        member.update()

        await inter.edit_original_message(content=loc.GetString("command-done-response"))
        _text = loc.GetString("note-command-log-issued", text=text, username=_member.name)
        Logger.high(inter, _text)
        Logger.secret(inter, _text)