import os
from pathlib import Path
import disnake
from disnake.ext import commands

import src.Events as Events
from src.Config import *
from src.Classes import Project, TagTypes, Tag, SubscribePost
from src.Tools import get_projects
from src.Logger import *
from src.Connect import getUserid
from src.Localization import LocalizationManager
from src.HelpManager import HelpManager


def add_config_commands(bot: commands.InteractionBot):
    helper = HelpManager()
    loc = LocalizationManager()
    disabled_commands = from_toml("config", "Commands")
    if not disabled_commands: disabled_commands = {}

    if "create-project" not in disabled_commands or disabled_commands["create-project"]:
        @bot.slash_command(
            name=loc.GetString("create-project-command-name"),
            description=loc.GetString("create-project-command-description")
            )
        async def create_project(
            inter: disnake.ApplicationCommandInteraction,
            name: str = commands.Param(
                name=loc.GetString("create-project-command-param-name-name"),
                description=loc.GetString("create-project-command-param-name-description"),
                min_length=1,
                max_length=50
            ),
            maxBrigPerUser: int = commands.Param(
                name=loc.GetString("create-project-command-param-maxbrigperuser-name"),
                description=loc.GetString("create-project-command-param-maxbrigperuser-description"),
                min_value=1
            ),
            forum: disnake.channel.ForumChannel = commands.Param(
                name=loc.GetString("create-project-command-param-forum-name"),
                description=loc.GetString("create-project-command-param-forum-description")
            ),
            waiterRole: disnake.Role = commands.Param(
                name=loc.GetString("create-project-command-param-waiterrole-name"),
                description=loc.GetString("create-project-command-param-waiterrole-description"),
                default=None
            ),
            mainChannel: disnake.TextChannel = commands.Param(
                name=loc.GetString("create-project-command-param-mainchannel-name"),
                description=loc.GetString("create-project-command-param-mainchannel-description")
            ),
            statChannel: disnake.TextChannel = commands.Param(
                name=loc.GetString("create-project-command-param-statchannel-name"),
                description=loc.GetString("create-project-command-param-statchannel-description")
            )):
            await inter.response.defer(ephemeral=True)
            if name not in get_projects():
                project = Project(bot, name)
                project.maxBrigPerUser = maxBrigPerUser
                project.forum = forum
                project.mainChannel = mainChannel
                project.statChannel = statChannel
                project.waiterRole = waiterRole
                project.write_project_info()

                await inter.edit_original_message(loc.GetString("command-done-response"))
                Logger.medium(inter, loc.GetString("create-project-command-done-log", project=name))

            else: await inter.edit_original_message(loc.GetString("create-project-command-project-exist-error"))
        helper.AddCommand(create_project)


    if "change-project" not in disabled_commands or disabled_commands["change-project"]:
        @bot.slash_command(
            name=loc.GetString("change-project-command-name"),
            description=loc.GetString("change-project-command-description")
        )
        async def change_project(
            inter: disnake.ApplicationCommandInteraction,
            projectName: str = commands.Param(
                name=loc.GetString("change-project-command-param-projectname-name"),
                description=loc.GetString("change-project-command-param-projectname-description"),
                choices=get_projects()
            ),
            maxBrigPerUser: int = commands.Param(
                name=loc.GetString("change-project-command-param-maxbrigperuser-name"),
                description=loc.GetString("change-project-command-param-maxbrigperuser-description"),
                min_value=1,
                default=None
            ),
            forum: disnake.channel.ForumChannel = commands.Param(
                name=loc.GetString("change-project-command-param-forum-name"),
                description=loc.GetString("change-project-command-param-forum-description"),
                default=None
            ),
            waiterRole: disnake.Role = commands.Param(
                name=loc.GetString("change-project-command-param-waiterrole-name"),
                description=loc.GetString("change-project-command-param-waiterrole-description"),
                default=None
            ),
            mainChannel: disnake.TextChannel = commands.Param(
                name=loc.GetString("change-project-command-param-mainchannel-name"),
                description=loc.GetString("change-project-command-param-mainchannel-description"),
                default=None
            ),
            statChannel: disnake.TextChannel = commands.Param(
                name=loc.GetString("change-project-command-param-statchannel-name"),
                description=loc.GetString("change-project-command-param-statchannel-description"),
                default=None
            )):
            await inter.response.defer(ephemeral=True)
            project = Project(bot, projectName)
            await project.read_project_info()

            if maxBrigPerUser is not None: project.maxBrigPerUser = maxBrigPerUser
            if forum is not None: project.forum = forum
            if waiterRole is not None: project.waiterRole = waiterRole
            if mainChannel is not None: project.mainChannel = mainChannel
            if statChannel is not None: project.statChannel = statChannel

            await inter.edit_original_message(loc.GetString("command-done-response"))
            Logger.low(inter, loc.GetString("change-project-command-done-log", project=projectName))
            Events.onProjectInfoChanged.raiseEvent(project)
        helper.AddCommand(change_project)


    if "create-tag" not in disabled_commands or disabled_commands["create-tag"]:
        @bot.slash_command(
            name=loc.GetString("create-tag-command-name"),
            description=loc.GetString("create-tag-command-description")
        )
        async def create_tag(
            inter: disnake.ApplicationCommandInteraction,
            projectName: str = commands.Param(
                name=loc.GetString('create-tag-command-param-projectname-name'),
                description=loc.GetString('create-tag-command-param-projectname-description'),
                choices=get_projects()
            ),
            name: str = commands.Param(
                name=loc.GetString('create-tag-command-param-name-name'),
                description=loc.GetString('create-tag-command-param-name-description')
            ),
            tagType: str = commands.Param(
                name=loc.GetString("create-tag-command-param-tagtype-name"),
                description=loc.GetString("create-tag-command-param-tagtype-description"),
                choices=[e.value for e in TagTypes]
            ),
            ping: disnake.Role = commands.Param(
                name=loc.GetString("create-tag-command-param-ping-name"),
                description=loc.GetString("create-tag-command-param-ping-description"),
                default=0
            ),
            score: int = commands.Param(
                name=loc.GetString('create-tag-command-param-score-name'),
                description=loc.GetString('create-tag-command-param-score-description'),
                default=0
            ),
            maxMemebers: int = commands.Param(
                name=loc.GetString('create-tag-command-param-maxmemebers-name'),
                description=loc.GetString('create-tag-command-param-maxmemebers-description'),
                default=0
            )):
            await inter.response.defer(ephemeral=True)
            project = Project(bot, projectName)
            await project.read_project_info()

            disTag = project.forum.get_tag_by_name(name)
            if disTag is not None:
                tag = Tag(disTag, project)
                tag.tagType = TagTypes(tagType)
                tag.ping = ping
                tag.scoreModifier = score
                tag.maxMembers = maxMemebers
                tag.write_tag()

                await inter.edit_original_message(loc.GetString("command-done-response"))
                Logger.low(inter, loc.GetString("create-tag-command-done-log", name=name, projectName=projectName))

            else:
                await inter.edit_original_message(loc.GetString("teg-create-command-error"))
        helper.AddCommand(create_tag)


    if "delete-tag" not in disabled_commands or disabled_commands["delete-tag"]:
        @bot.slash_command(
            name=loc.GetString("delete-tag-command-name"),
            description=loc.GetString("delete-tag-command-description")
        )
        async def delete_tag(
            inter: disnake.ApplicationCommandInteraction,
            projectName: str = commands.Param(
                name=loc.GetString('delete-tag-command-param-projectname-name'),
                description=loc.GetString('delete-tag-command-param-projectname-description'),
                choices=get_projects()
            ),
            name: str = commands.Param(
                name=loc.GetString('delete-tag-command-param-name-name'),
                description=loc.GetString('delete-tag-command-param-name-description')
            )):
            await inter.response.defer(ephemeral=True)
            project = Project(bot, projectName)
            await project.read_project_info()

            disTag = project.forum.get_tag_by_name(name)
            if disTag is not None:
                project.delete_tag(Tag(disTag, project))
                await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
                Logger.medium(inter, loc.GetString("delete-tag-command-done-log", name=name, projectName=projectName))
            else:
                await inter.edit_original_message(loc.GetString("teg-delete-command-error"))
        helper.AddCommand(delete_tag)

    if "change-project-roles" not in disabled_commands or disabled_commands["change-project-roles"]:
        @bot.slash_command(
            name=loc.GetString("change-project-roles-command-name"),
            description=loc.GetString("change-project-roles-command-description")
        )
        async def change_project_roles(
            inter: disnake.ApplicationCommandInteraction,
            projectName: str = commands.Param(
                name=loc.GetString('change-project-roles-command-param-projectname-name'),
                description=loc.GetString('change-project-roles-command-param-projectname-description'),
                choices=get_projects()
            ),
            mode: str = commands.Param(
                name=loc.GetString('change-project-roles-command-param-mode-name'),
                description=loc.GetString("change-project-roles-command-param-mode-description"),
                choices=[
                    loc.GetString("add"),
                    loc.GetString("remove")
                ]
            ),
            role: disnake.Role = commands.Param(
                name=loc.GetString("change-project-roles-command-param-role-name")
            )):
            await inter.response.defer(ephemeral=True)
            project = Project(bot, projectName)
            await project.read_project_info()

            if mode == loc.GetString("add"):
                project.associatedRoles.append(role)
                Logger.low(inter, loc.GetString("change-project-roles-command-done-log-add", role=role.name, projectName=projectName))
            elif role in project.associatedRoles:
                project.associatedRoles.remove(role)
                Logger.low(inter, loc.GetString("change-project-roles-command-done-log-remove", role=role.name, projectName=projectName))
            Events.onProjectInfoChanged.raiseEvent(project)

            await inter.edit_original_message(loc.GetString("command-done-response"))
        helper.AddCommand(change_project_roles)


    if "project-config" not in disabled_commands or disabled_commands["project-config"]:
        @bot.slash_command(
            name=loc.GetString("project-config-command-name"),
            description=loc.GetString("project-config-command-description")
        )
        async def project_config(
            inter: disnake.ApplicationCommandInteraction,
            projectName: str = commands.Param(
                name=loc.GetString('project-config-command-param-projectname-name'),
                description=loc.GetString('project-config-command-param-projectname-description'),
                choices=get_projects()
            )):
            await inter.response.defer(ephemeral=True)
            project = Project(bot, projectName)
            await inter.edit_original_message(embed=project.config_embed())
        helper.AddCommand(project_config)


    if "create-roles-post" not in disabled_commands or disabled_commands["create-roles-post"]:
        @bot.slash_command(
            name=loc.GetString("create-roles-post-command-name"),
            description=loc.GetString("create-roles-post-command-description")
        )
        async def create_roles_post(
            inter: disnake.ApplicationCommandInteraction,
            channel: disnake.TextChannel = commands.Param(
                name=loc.GetString("create-roles-post-command-param-channel-name"),
                description=loc.GetString("create-roles-post-command-param-channel-description")
            )):
            await inter.response.defer(ephemeral=True)
            message = await inter.channel.send("Wait...")

            bot.subPosts[message.jump_url] = SubscribePost(bot, message)
            bot.subPosts[message.jump_url].update()
        helper.AddCommand(create_roles_post)


    if "change-roles-post" not in disabled_commands or disabled_commands["change-roles-post"]:
        @bot.slash_command(
            name=loc.GetString("change-roles-post-command-name"),
            description=loc.GetString("change-roles-post-command-description")
        )
        async def change_roles_post(
            inter: disnake.ApplicationCommandInteraction,
            url: str = commands.Param(
                name=loc.GetString('change-roles-post-command-param-url-name'),
                description=loc.GetString('change-roles-post-command-param-url-description')
            ),
            categorie: str = commands.Param(
                name=loc.GetString('change-roles-post-command-param-categorie-name'),
                description=loc.GetString('change-roles-post-command-param-categorie-description')
            ),
            emoji: str = commands.Param(
                name=loc.GetString('change-roles-post-command-param-emoji-name'),
                description=loc.GetString('change-roles-post-command-param-emoji-description')
            ),
            text: str = commands.Param(
                name=loc.GetString('change-roles-post-command-param-text-name'),
                description=loc.GetString('change-roles-post-command-param-text-description'),
                default=""
            ),
            role: disnake.Role = commands.Param(
                name=loc.GetString('change-roles-post-command-param-role-name'),
                description=loc.GetString('change-roles-post-command-param-role-description'),
                default=None
            )):
            await inter.response.defer(ephemeral=True)

            if url not in bot.subPosts:
                await inter.edit_original_message(loc.GetString("change-roles-post-command-url-error"))
                return

            if role: bot.subPosts[url].add_role(categorie, emoji, text, role)
            else: bot.subPosts[url].rem_role(categorie, emoji)

            await inter.edit_original_message(loc.GetString("command-done-response"))
        helper.AddCommand(change_roles_post)


    if "unload-config" not in disabled_commands or disabled_commands["unload-config"]:
        @bot.slash_command(
            name=loc.GetString("unload-config-command-name"),
            description=loc.GetString("unload-config-command-description")
        )
        async def unload_config(
            inter: disnake.ApplicationCommandInteraction
            ):
            await inter.response.defer(ephemeral=True)
            await inter.edit_original_message(view=DropDownView(get_data_path().name, get_data_path()))
        helper.AddCommand(unload_config)


    if "load-config" not in disabled_commands or disabled_commands["load-config"]:
        @bot.slash_command(
            name=loc.GetString("load-config-command-name"),
            description=loc.GetString("load-config-command-description")
        )
        async def load_config(
            inter: disnake.ApplicationCommandInteraction,
            fileToUpload: disnake.Attachment = commands.Param(
                name=loc.GetString("load-config-command-param-filetoupload-name"),
                description=loc.GetString("load-config-command-param-filetoupload-description")
            ),
            path: str = commands.Param(
                name=loc.GetString("load-config-command-param-path-name"),
                description=loc.GetString("load-config-command-param-path-description"),
                default=""
            )):
            await inter.response.defer(ephemeral=True)
            path = get_data_path() / path / fileToUpload.filename

            with open(path, "wb") as f:
                f.write(await fileToUpload.read())
                Logger.high(inter, loc.GetString("load-config-command-done-log", fileToUpload=fileToUpload.filename, path=str(path)))
            await inter.edit_original_message(content=loc.GetString("command-done-response"))
            await bot.restart()
        helper.AddCommand(load_config)


    if "reboot" not in disabled_commands or disabled_commands["reboot"]:
        @bot.slash_command(
            name=loc.GetString("reboot-command-name"),
            description=loc.GetString("reboot-command-description")
        )
        async def reboot(inter: disnake.ApplicationCommandInteraction):
            await inter.response.defer(ephemeral=True)
            await inter.edit_original_message(content=loc.GetString("command-done-response"))
            await bot.restart()
        helper.AddCommand(reboot)


    if "user-id" not in disabled_commands or disabled_commands["user-id"]:
        @bot.slash_command(
            name=loc.GetString("user-id-command-name"),
            description=loc.GetString("user-id-command-description")
        )
        async def user_id(
            inter: disnake.ApplicationCommandInteraction,
            ckey: str = commands.Param(
                name=loc.GetString("user-id-command-param-ckey-name"),
                description=loc.GetString("user-id-command-param-ckey-description")
            )):
            await inter.response.defer(ephemeral=True)
            await inter.edit_original_message(content=f"```{getUserid(ckey)}```")
            Logger.medium(inter, loc.GetString("user-id-command-done-log", ckey=ckey))
        helper.AddCommand(user_id)


# region View
    class UnloadConfigDropdown(disnake.ui.StringSelect):
        def __init__(self, root: str, path: Path):
            loc = LocalizationManager()

            self.root = root
            self.path = path
            options = []
            for _dir in self.path.iterdir():
                if (_dir.name == '../' and root == self.path.parent.name) or len(options) == 25 or _dir.name.startswith('.'):
                    continue
                options.append(disnake.SelectOption(
                    label=_dir.name,
                    value=_dir.name
                ))

            super().__init__(
                placeholder=loc.GetString("unload-config-dropdown-placeholder"),
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            value = inter.values[0]
            if value != '../': self.path = self.path / value
            else: self.path = self.path.parent

            if self.path.is_file():
                await inter.send(file=disnake.File(str(self.path)), ephemeral=True)
                Logger.medium(inter, loc.GetString("unload-config-command-done-log", configFile=self.path.name))
                return

            await inter.send(view=DropDownView(self.root, self.path), ephemeral=True)


    class DropDownView(disnake.ui.View):
        def __init__(self, root: str, path: Path):
            super().__init__()
            self.add_item(UnloadConfigDropdown(root, path))
# endregion

