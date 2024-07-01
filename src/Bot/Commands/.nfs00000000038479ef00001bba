import os
import disnake
from disnake.ext import commands

from src.Logger import *
from src.Classes import Member
from src.Config import get_data_path
from src.Connect import unload


def add_save_commands(bot: disnake.Client):
    @bot.slash_command(
        name = "привязать-папку",
        description = "Привязать личную папку пользователя."
    )
    async def link_folder(
        inter: disnake.CommandInteraction,
        folder: str = commands.Param(
            name="папка",
            description="название личной папки."
        )):
        member = Member(inter.author)
        if member.folder_is_empty():
            member.change_folder(folder.replace("/", "").replace(" ", ""))
            await inter.send(content="**Папка успешно привязана**", ephemeral=True)
            Logger.medium(inter, f"привязана папка {folder}")
        else:
            await inter.send(content=f'**Вы уже имеете привязанную папку "{member.ownFolder}". Если вам нужно изменить папку обратитесь к ведущему мапперу.**', ephemeral=True)


    @bot.slash_command(
        name = "изменить-папку",
        description = "Изменить личную папку пользователя."
    )
    async def change_folder(
        inter: disnake.CommandInteraction,
        member: disnake.Member = commands.Param(
            name='пользователь',
            description='Пользователь, папку которого нужно изменить.'
        ),
        folder: str = commands.Param(
            name="папка",
            description="название новой папки."
        )):
        Member(member).change_folder(folder)
        await inter.send(content=f"**Done**", ephemeral=True)
        Logger.medium(inter, f"изменена личная папка на {folder}")


    async def unload_save(
        inter: disnake.AppCommandInteraction,
        path: str = commands.Param(
            name="путь",
            description="путь до сейва относительно личной папки."
        ),
        fromFolder: bool = True
        ):
        await inter.response.defer(ephemeral=True)
        full_path = get_data_path() + path.split("/")[-1]

        if fromFolder:
            member = Member(inter.author)
            if member.folder_is_empty():
                await inter.send(content="Вы не привязали личную папку, чтобы скачивать сейвы, пропишите команду /привязать-папку.", ephemeral=True)
                return
            
            if ".." in path.split("/"): 
                await inter.send(content='Недопустимый символ ".." в пути к файлу.', ephemeral=True)
                return

            unload(url=path, folder=member.ownFolder)
            Logger.low(inter, f"скачан сейв по пути /{member.ownFolder}/{path}")
        else:
            unload(url=path)
            Logger.medium(inter, f"скачан сейв по пути {path}")

        await inter.edit_original_message(file=disnake.File(full_path))
        os.remove(full_path)


    @bot.slash_command(
        name="сейв",
        description="Скачать сейв из привязанной папки по пути."
    )
    async def save(
        inter: disnake.AppCommandInteraction,
        path: str = commands.Param(
            name="путь",
            description="путь до сейва относительно личной папки."
        )):
        await unload_save(inter, path)


    @bot.slash_command(
        name="сейв-плюс",
        description="Скачать сейв из привязанной папки по пути."
    )
    async def save_plus(
        inter: disnake.AppCommandInteraction,
        path: str = commands.Param(
            name="путь",
            description="путь до сейва."
        )):
        await unload_save(inter, path, False)