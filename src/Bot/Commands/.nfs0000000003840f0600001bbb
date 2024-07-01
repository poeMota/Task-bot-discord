import disnake
from disnake.ext import commands

from src.Logger import *


def add_fun_commands(bot: disnake.Client):
    @bot.slash_command(
        name="отправить",
        description="Отправить текст от лица бота."
    )
    async def bot_send(
        inter: disnake.CommandInteraction,
        text: str = commands.Param(
            name="текст",
            description="текст, который нужно отправить от лица бота"
        )):
        await inter.send(content="**Done**", ephemeral=True)
        response = await inter.original_response()
        await inter.channel.send(text)
        await response.delete()
        Logger.low(inter, "отправлено сообщение от лица бота")
    

    @bot.slash_command(
        name="когда",
        description="Через час."
    )
    async def when(inter: disnake.CommandInteraction):
        await bot_send(inter, "Через час")