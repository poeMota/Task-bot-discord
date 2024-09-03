import disnake
from disnake.ext import commands

from src.Logger import *
from src.Localization import LocalizationManager


def add_fun_commands(bot: disnake.Client):
    loc = LocalizationManager()

    @bot.slash_command(
        name=loc.GetString("bot-send-command-name"),
        description=loc.GetString("bot-send-command-description")
    )
    async def bot_send(
        inter: disnake.CommandInteraction,
        text: str = commands.Param(
            name=loc.GetString("bot-send-command-param-text-name"),
            description=loc.GetString("bot-send-command-param-text-description")
        )):
        await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
        response = await inter.original_response()
        await inter.channel.send(text.replace("\\n", '\n'))
        await response.delete()
        Logger.low(inter, loc.GetString("bot-send-command-done-log", text=text))
    

    @bot.slash_command(
        name=loc.GetString("when_command_name"),
        description=loc.GetString("when_command_description")
    )
    async def when(inter: disnake.CommandInteraction):
        await bot_send(inter, loc.GetString("when_command_response"))