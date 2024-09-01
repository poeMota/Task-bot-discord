import os
import disnake
from disnake.ext import commands

from src.Logger import *
from src.Classes import Member
from src.Config import get_data_path
from src.Connect import unload, getDirs


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
        path: str,
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

            try:
                unload(url=path, folder=member.ownFolder)
                Logger.low(inter, f"скачан сейв по пути /{member.ownFolder}/{path}")
            except IsADirectoryError as e:
                await inter.edit_original_message(content=f"**[Ошибка]** Вы питаетесь скачать папку, а не файл, проверьте правильность указанного вами пути.")
                Logger.high(inter, f"ошибка при скачивании сейва по пути {path}: {repr(e)}")
                return
        else:
            try:
                unload(url=path)
                Logger.medium(inter, f"скачан сейв по пути {path}")
            except IsADirectoryError as e:
                await inter.edit_original_message(content=f"**[Ошибка]** Вы питаетесь скачать папку, а не файл, проверьте правильность указанного вами пути.")
                Logger.high(inter, f"ошибка при скачивании сейва по пути {path}: {repr(e)}")
                return

        await inter.edit_original_message(file=disnake.File(full_path))
        os.remove(full_path)
    

    async def unload_dropdown_save(
            inter: disnake.AppCommandInteraction,
            path: str,
            fromFolder: bool = True
            ):
            if fromFolder:
                member = Member(inter.author)
                if not member.folder_is_empty():
                    await inter.response.defer(ephemeral=True)
                    await inter.edit_original_message(content=f"# Скачайте сейв с помощью меню поиска:", view=DropDownView(
                                                        root=member.ownFolder, 
                                                        path=f"{member.ownFolder}/{path.strip()}"))
                else:
                    await inter.send(content="Вы не привязали личную папку, чтобы скачивать сейвы, пропишите команду /привязать-папку.", ephemeral=True)
            else:
                await inter.response.defer(ephemeral=True)
                await inter.edit_original_message(content=f"# Скачайте сейв с помощью меню поиска:", view=DropDownView(
                                                        root="",
                                                        path=path.strip()))


    @bot.slash_command(
        name="сейв",
        description="Скачать сейв из привязанной папки по пути."
    )
    async def save(
        inter: disnake.AppCommandInteraction,
        path: str = commands.Param(
            name="путь",
            description="путь до сейва относительно личной папки.",
            default=""
        )):
        if not path.strip() or path.endswith("/"):
            await unload_dropdown_save(inter, path)
            return
        
        await unload_save(inter, path)


    @bot.slash_command(
        name="сейв-плюс",
        description="Скачать сейв из привязанной папки по пути."
    )
    async def save_plus(
        inter: disnake.AppCommandInteraction,
        path: str = commands.Param(
            name="путь",
            description="путь до сейва.",
            default=""
        )):
        if not path.strip() or path.endswith("/"):
            await unload_dropdown_save(inter, path, False)
            return
        
        await unload_save(inter, path, False)


# region View
    class SaveDropdown(disnake.ui.StringSelect):
        def __init__(self, root: str, path: str):
            self.root = root
            self.path = f"{path.replace("//", '/').removesuffix('/')}/".split('/')
            options = []
            for _dir in getDirs('/'.join(self.path)):
                if (_dir == '../' and root == self.path[-2]) or len(options) == 25:
                    continue
                options.append(disnake.SelectOption(
                    label=_dir,
                    value=_dir
                ))

            super().__init__(
                placeholder=f"Выберите путь до файла.",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            value = inter.values[0]
            _path = list(self.path)
            if value != '../': _path += [value]
            else: del _path[-2]

            if not value.endswith('/'):
                await unload_save(inter, '/'.join(_path))
                return

            await inter.send(view=DropDownView(self.root, '/'.join(_path)), ephemeral=True)


    class DropDownView(disnake.ui.View):
        def __init__(self, root: str, path: str):
            super().__init__()
            self.add_item(SaveDropdown(root, path))
# endregion