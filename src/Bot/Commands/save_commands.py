import os
import disnake
from disnake.ext import commands

from src.Logger import *
from src.Classes import Member
from src.Config import get_data_path
from src.Connect import *
from src.Localization import LocalizationManager
from src.HelpManager import HelpManager


def add_save_commands(bot: disnake.Client):
    loc = LocalizationManager()
    helper = HelpManager()

    disabled_commands = from_toml("config", "Commands")
    if not disabled_commands: disabled_commands = {}

    if "link-folder" not in disabled_commands or disabled_commands["link-folder"]:
        @bot.slash_command(
            name=loc.GetString("link-folder-command-name"),
            description=loc.GetString("link-folder-command-description")
        )
        async def link_folder(
            inter: disnake.CommandInteraction,
            folder: str = commands.Param(
                name=loc.GetString("link-folder-command-param-folder-name"),
                description=loc.GetString("link-folder-command-param-folder-description")
            )):
            await inter.response,defer(ephemeral=True)

            member = Member(inter.author)
            if member.folder_is_empty():

                folder = folder.replace("/", "").replace(" ", "")
                for mem in bot.guild().members:
                    if Member(mem).ownFolder == folder:
                        await inter.edit_original_message(content=loc.GetString("link-folder-command-stranger-folder-response"))
                        Logger.secret(inter, loc.GetString("link-folder-command-stranger-folder-log",
                                                           folder=folder,
                                                           member1=inter.author.id,
                                                           member2=mem.id))
                        return

                member.change_folder(folder)
                await inter.edit_original_message(content=loc.GetString("link-folder-command-success-response"))
                Logger.medium(inter, loc.GetString("link-folder-command-log-folder-linked", folder=folder))
            else:
                await inter.edit_original_message(content=loc.GetString("link-folder-command-already-linked-response", folder=member.ownFolder))
        helper.AddCommand(link_folder)


    if "change-folder" not in disabled_commands or disabled_commands["change-folder"]:
        @bot.slash_command(
            name=loc.GetString("change-folder-command-name"),
            description=loc.GetString("change-folder-command-description")
        )
        async def change_folder(
            inter: disnake.CommandInteraction,
            member: disnake.Member = commands.Param(
                name=loc.GetString("change-folder-command-param-member-name"),
                description=loc.GetString("change-folder-command-param-member-description")
            ),
            folder: str = commands.Param(
                name=loc.GetString("change-folder-command-param-folder-name"),
                description=loc.GetString("change-folder-command-param-folder-description")
            )):
            Member(member).change_folder(folder)
            await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
            Logger.medium(inter, loc.GetString("change-folder-command-log-folder-changed", folder=folder))
        helper.AddCommand(change_folder)


    async def unload_save(
        inter: disnake.AppCommandInteraction,
        path: str,
        fromFolder: bool = True
        ):
        await inter.response.defer(ephemeral=True)
        full_path = str(get_data_path() / path.split("/")[-1])

        if fromFolder:
            member = Member(inter.author)

            if not isValidUrl(path.strip(), member.ownFolder):
                print(path.strip(), member.ownFolder)
                await inter.send(content=loc.GetString("unload-save-command-invalid-path-error"), ephemeral=True)
                return

            if member.folder_is_empty():
                await inter.send(content=loc.GetString("unload-save-command-no-folder-error"), ephemeral=True)
                return

            if ".." in path.split("/"):
                await inter.send(content=loc.GetString("unload-save-command-invalid-symbol-error"), ephemeral=True)
                return

            try:
                unload(url=path, folder=member.ownFolder)
                Logger.low(inter, loc.GetString("unload-save-command-log-save-downloaded", path=path))
            except IsADirectoryError as e:
                await inter.edit_original_message(content=loc.GetString("unload-save-command-folder-error"))
                Logger.high(inter, loc.GetString("unload-save-command-log-directory-error", path=path, error=repr(e)))
                return
        else:
            if not isValidUrl(path.strip()):
                await inter.send(content=loc.GetString("unload-save-command-invalid-path-error"), ephemeral=True)
                return

            try:
                unload(url=path)
                Logger.medium(inter, loc.GetString("unload-save-command-log-save-downloaded", path=path))
            except IsADirectoryError as e:
                await inter.edit_original_message(content=loc.GetString("unload-save-command-folder-error"))
                Logger.high(inter, loc.GetString("unload-save-command-log-directory-error", path=path, error=repr(e)))
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

            if not isValidUrl(path.strip(), member.ownFolder):
                await inter.send(content=loc.GetString("unload-save-command-invalid-path-error"), ephemeral=True)
                return

            if not member.folder_is_empty():
                await inter.response.defer(ephemeral=True)
                await inter.edit_original_message(content=loc.GetString("unload-dropdown-save-command-menu-prompt"), view=DropDownView(
                                                    root=member.ownFolder.split('/')[-1],
                                                    path=f"{member.ownFolder}/{path.strip()}"))
            else:
                await inter.send(content=loc.GetString("unload-save-command-no-folder-error"), ephemeral=True)
        else:
            if not isValidUrl(path.strip()):
                await inter.send(content=loc.GetString("unload-save-command-invalid-path-error"), ephemeral=True)
                return

            await inter.response.defer(ephemeral=True)
            await inter.edit_original_message(content=loc.GetString("unload-dropdown-save-command-menu-prompt"), view=DropDownView(
                                                    root="",
                                                    path=path.strip()))


    if "save" not in disabled_commands or disabled_commands["save"]:
        @bot.slash_command(
            name=loc.GetString("save-command-name"),
            description=loc.GetString("save-command-description")
        )
        async def save(
            inter: disnake.AppCommandInteraction,
            path: str = commands.Param(
                name=loc.GetString("save-command-param-path-name"),
                description=loc.GetString("save-command-param-path-description"),
                default=""
            )):
            if not path.strip() or path.endswith("/"):
                await unload_dropdown_save(inter, path)
                return

            await unload_save(inter, path)
        helper.AddCommand(save)


    if "save-plus" not in disabled_commands or disabled_commands["save-plus"]:
        @bot.slash_command(
            name=loc.GetString("save-plus-command-name"),
            description=loc.GetString("save-plus-command-description")
        )
        async def save_plus(
            inter: disnake.AppCommandInteraction,
            path: str = commands.Param(
                name=loc.GetString("save-plus-command-param-path-name"),
                description=loc.GetString("save-plus-command-param-path-description"),
                default=""
            )):
            if not path.strip() or path.endswith("/"):
                await unload_dropdown_save(inter, path, False)
                return

            await unload_save(inter, path, False)
        helper.AddCommand(save_plus)


# region View
    class SaveDropdown(disnake.ui.StringSelect):
        def __init__(self, root: str, path: str):
            loc = LocalizationManager()

            self.root = root
            self.path = f"{path.replace("//", '/').removesuffix('/')}/".split('/')
            options = []

            dates = fileDates('/'.join(self.path))
            for _dir in dates:
                if (_dir == '../' and root == self.path[-2]) or len(options) == 25:
                    continue
                options.append(disnake.SelectOption(
                    label=_dir,
                    value=_dir,
                    description=dates[_dir]
                ))

            super().__init__(
                placeholder=loc.GetString("save_dropdown_placeholder"),
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

