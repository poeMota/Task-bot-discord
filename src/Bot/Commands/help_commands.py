import math
import asyncio
import disnake
from disnake.ext import commands

from src.Logger import *
from src.Localization import LocalizationManager
from src.HelpManager import HelpManager


def add_help_commands(bot: disnake.Client):
    loc = LocalizationManager()
    helper = HelpManager()

    @bot.slash_command(
        name=loc.GetString("help-all-command-name").lower(),
        description=loc.GetString("help-all-command-description")
    )
    async def help_all(
        inter: disnake.CommandInteraction,
        toAll: bool = commands.Param(
            name=loc.GetString("help-all-command-param-toall-name"),
            description=loc.GetString("help-all-command-param-toall-description"),
            default=False
        )):
        maxEmbeds = 8

        embeds = helper.GetCommandsHelp()
        for i in range(math.ceil(len(embeds) / maxEmbeds)):
            await inter.send(embeds=embeds[i * maxEmbeds:i * maxEmbeds + maxEmbeds], ephemeral=not toAll)
            if toAll: await asyncio.sleep(1)
        
        Logger.low(inter, loc.GetString("help-all-command-log-viewed"))
    

    helper.AddCommands([
        help_all
    ])