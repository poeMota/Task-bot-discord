import disnake
from disnake.ext import commands

from src.Logger import *
from src.Config import *
from src.Localization import LocalizationManager
from src.HelpManager import HelpManager


def add_fun_commands(bot: disnake.Client):
    loc = LocalizationManager()
    helper = HelpManager()

    disabled_commands = from_toml("config", "Commands")
    if not disabled_commands: disabled_commands = {}

    if "bot-send" not in disabled_commands or disabled_commands["bot-send"]:
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
        helper.AddCommand(bot_send)


    if "when" not in disabled_commands or disabled_commands["when"]:
        @bot.slash_command(
            name=loc.GetString("when-command-name"),
            description=loc.GetString("when-command-description")
        )
        async def when(inter: disnake.CommandInteraction):
            await bot_send(inter, loc.GetString("when-command-response"))
        helper.AddCommand(when)

