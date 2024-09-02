import disnake
from disnake.ext import commands

import src.Events as Events
from src.Config import *
from src.Classes import Project, TagTypes, Tag
from src.Tools import get_projects, data_files
from src.Logger import *
from src.Connect import getHWID
from src.Localization import LocalizationManager


def add_config_commands(bot: commands.InteractionBot):
    loc = LocalizationManager()

    @bot.slash_command(
        name="создать-проект",
        description="Создать базу данных для подпроекта."
    )
    async def create_project(
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(
            name='проект',
            description='Название проекта.',
            min_length=1,
            max_length=50
        ),
        maxBrigPerUser: int = commands.Param(
            name='бригад',
            description='Максимальное количество бригад для одного пользователя.',
            min_value=1
        ),
        forum: disnake.channel.ForumChannel = commands.Param(
            name='форум',
            description='Канал с заказами для проекта.'
        ),
        waiterRole: disnake.Role = commands.Param(
            name='ждун',
            description='Роль, которую будет пинговать при создании тасков.'
        ),
        mainChannel: disnake.TextChannel = commands.Param(
            name='канал',
            description='Основной канал (рабочий чат) проекта.'
        ),
        statChannel: disnake.TextChannel = commands.Param(
            name='статистика',
            description='Канал, куда будет отправлятся статистика рабочих.'
        )):
        if name not in get_projects():
            project = Project(bot, name)
            project.maxBrigPerUser = maxBrigPerUser
            project.forum = forum
            project.mainChannel = mainChannel
            project.statChannel = statChannel
            project.waiterRole = waiterRole
            project.write_project_info()

            await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
            Logger.medium(inter, f"создан проект {name}")

        else: await inter.send(content=loc.GetString("project-create-command-error"), ephemeral=True)


    @bot.slash_command(
        name="изменить-проект",
        description="Изменить конфиг подпроекта."
    )
    async def create_project(
        inter: disnake.ApplicationCommandInteraction,
        projectName: str = commands.Param(
            name='проект',
            description='Название проекта, конфиг которого надо изменить.',
            choices=get_projects()
        ),
        maxBrigPerUser: int = commands.Param(
            name='бригад',
            description='Максимальное количество бригад для одного пользователя.',
            min_value=1,
            default=None
        ),
        forum: disnake.channel.ForumChannel = commands.Param(
            name='форум',
            description='Канал с заказами для проекта.',
            default=None
        ),
        waiterRole: disnake.Role = commands.Param(
            name='ждун',
            description='Роль, которую будет пинговать при создании тасков.',
            default=None
        ),
        mainChannel: disnake.TextChannel = commands.Param(
            name='канал',
            description='Основной канал (рабочий чат) проекта.',
            default=None
        ),
        statChannel: disnake.TextChannel = commands.Param(
            name='статистика',
            description='Канал, куда будет отправлятся статистика рабочих.',
            default=None
        )):
        project = Project(bot, projectName)
        await project.read_project_info()

        if maxBrigPerUser is not None: project.maxBrigPerUser = maxBrigPerUser
        if forum is not None: project.forum = forum
        if waiterRole is not None: project.waiterRole = waiterRole
        if mainChannel is not None: project.mainChannel = mainChannel
        if statChannel is not None: project.statChannel = statChannel

        await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
        Logger.low(inter, f'изменён конфиг проекта {projectName}')
        Events.onProjectInfoChanged.raiseEvent(project)


    @bot.slash_command(
        name="создать-тег",
        description="подключить тег форму к функционалу бота."
    )
    async def create_tag(
        inter: disnake.ApplicationCommandInteraction,
        projectName: str = commands.Param(
            name='проект',
            description='Название проекта, для которого нужно добавить тег.',
            choices=get_projects()
        ),
        name: str = commands.Param(
            name='тег',
            description='название тега.'
        ),
        tagType: str = commands.Param(
            name="тип",
            description="тип тега",
            choices=[e.value for e in TagTypes]
        ),
        ping: disnake.Role = commands.Param(
            name="роль",
            description="роль, пингуемая тегом (если тег пинга).",
            default=0
        ),
        score: int = commands.Param(
            name='очки',
            description='(если тег сложности).',
            default= 0
        ),
        maxMemebers: int = commands.Param(
            name='пользоветелей',
            description='максимальное количество пользователей в бригаде, которое задаёт тег (если тег сложности).',
            default= 0
        )
    ):
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

            await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
            Logger.low(inter, f"создан тег {name} проекта {projectName}")

        else: await inter.send(content=loc.GetString("teg-create-command-error"), ephemeral=True)


    @bot.slash_command(
        name="удалить-тег",
        description="удалить тег из конфига проекта."
    )
    async def del_tag(
        inter: disnake.ApplicationCommandInteraction,
        projectName: str = commands.Param(
            name='проект',
            description='Название проекта, для которого нужно добавить тег.',
            choices=get_projects()
        ),
        name: str = commands.Param(
            name='тег',
            description='название тега.'
        )):
        project = Project(bot, projectName)
        await project.read_project_info()

        disTag = project.forum.get_tag_by_name(name)
        if disTag is not None:
            project.delete_tag(Tag(disTag, project))
            await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)
            Logger.medium(inter, f"удалён тег {name} проекта {projectName}")

        else: await inter.send(content=loc.GetString("teg-delete-command-error"), ephemeral=True)


    @bot.slash_command(
        name="изменить-роли-проекта",
        description="добавить роль к проекту."
    )
    async def change_project_roles(
        inter: disnake.ApplicationCommandInteraction,
        projectName: str = commands.Param(
            name='проект',
            description='Название проекта, роли которого нужно изменить.',
            choices=get_projects()
        ),
        mode: str = commands.Param(
            name='режим',
            description="Добавить или удалить роли проекта.",
            choices=["добавить", "удалить"]
        ),
        role: disnake.Role = commands.Param(
            name="роль"
        )):
        project = Project(bot, projectName)
        await project.read_project_info()

        if mode == "добавить":
            project.associatedRoles.append(role)
            Logger.low(inter, f"добавлена роль {role.name} для проекта {projectName}")
        elif role in project.associatedRoles:
            project.associatedRoles.remove(role)
            Logger.low(inter, f"удалена роль {role.name} из проекта {projectName}")
        Events.onProjectInfoChanged.raiseEvent(project)

        await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)


    @bot.slash_command(
        name="конфиг-проекта",
        description="показать конфиг проекта."
    )
    async def project_config(
        inter: disnake.ApplicationCommandInteraction,
        projectName: str = commands.Param(
            name='проект',
            description='Название проекта, конфиг которого нужно показать.',
            choices=get_projects()
        )):
        await inter.response.defer(ephemeral=True)
        project = Project(bot, projectName)
        await inter.edit_original_message(embed=project.config_embed())


    @bot.slash_command(
        name="изменить-пост-ролей",
        description="показать конфиг проекта."
    )
    async def change_roles_post(
        inter: disnake.ApplicationCommandInteraction,
        categorie: str = commands.Param(
            name='категория',
            description='Название категории.'
        ),
        emoji: str = commands.Param(
            name='емоджи',
            description='емоджи, которо будет выдавать роль.'
        ),
        text: str = commands.Param(
            name='текст',
            description='текст, который будет отображатся в посте у эмоджи.',
            default=""
        ),
        role: disnake.Role = commands.Param(
            name='роль',
            description='роль, которую нужно добавить для выдачи ролей (оставить пустым, если надо удалить).',
            default=None
        )):
        if role is not None: bot.subPost.add_role(categorie, emoji, text, role)
        else: bot.subPost.rem_role(categorie, emoji)
        await inter.send(content=loc.GetString("command-done-response"), ephemeral=True)


    @bot.slash_command(
        name="скачать-конфиг-файл",
        description="скачать конфиг файл бота"
    )
    async def unload_config(
        inter: disnake.ApplicationCommandInteraction,
        configFile: str = commands.Param(
            name="файл",
            description="название файла, который нужно скачать",
            choices=data_files()
        )):
        await inter.response.defer(ephemeral=True)
        Logger.medium(inter, f"скaчан файл конфига \"{configFile}\"")
        await inter.edit_original_message(file=disnake.File(get_data_path() + configFile))


    @bot.slash_command(
        name="загрузить-конфиг-файл",
        description="загрузить файл в постоянное хранилище бота"
    )
    async def load_config(
        inter: disnake.ApplicationCommandInteraction,
        fileToUpload: disnake.Attachment = commands.Param(
            name="файл",
            description="файл, который нужно загрузить"
        )):
        await inter.response.defer(ephemeral=True)
        with open(get_data_path() + fileToUpload.filename, "wb") as f:
            f.write(await fileToUpload.read())
            Logger.high(inter, f"загружен файл {fileToUpload.filename} в постоянное хранилище бота")
        await inter.edit_original_message(content=loc.GetString("command-done-response"))
        await bot.restart()


    @bot.slash_command(
        name="reboot"
    )
    async def reboot(inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        await bot.restart()
        await inter.edit_original_message(content=loc.GetString("command-done-response"))


    @bot.slash_command(
        name="hwid",
        description="Получить HWID пользователя"
    )
    async def hwid(
        inter: disnake.ApplicationCommandInteraction,
        ckey: str = commands.Param(
            name="ckey",
            description="ckey пользователя, HWID которого нужно получить"
        )):
        await inter.response.defer(ephemeral=True)
        await inter.edit_original_message(content=f"```{getHWID(ckey)}```")
        Logger.medium(inter, f"получен HWID по ckey - {ckey}")

