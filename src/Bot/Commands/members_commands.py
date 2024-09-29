import disnake
from disnake.ext import commands

from src.Tools import get_projects
from src.Classes import Member
from src.Logger import *
from src.Config import *
from src.Localization import LocalizationManager
from src.HelpManager import HelpManager


def add_members_commands(bot: disnake.Client):
    loc = LocalizationManager()
    helper = HelpManager()

    disabled_commands = from_toml("config", "Commands")
    if not disabled_commands: disabled_commands = {}

    if "change-score" not in disabled_commands or disabled_commands["change-score"]:
        @bot.slash_command(
            name=loc.GetString("change-score-command-name"),
            description=loc.GetString("change-score-command-description")
        )
        async def change_score(
            inter: disnake.CommandInteraction,
            mem: disnake.Member = commands.Param(
                name=loc.GetString('change-score-command-param-mem-name'),
                description=loc.GetString('change-score-command-param-mem-description')
            ),
            score: int = commands.Param(
                name=loc.GetString('change-score-command-param-score-name'),
                description=loc.GetString('change-score-command-param-score-description')
            )):
            member = Member(mem)
            if score >= 0:
                member.change_score(score, True)
            else:
                member.change_score(score, False)
            await inter.send(content=loc.GetString('change-score-command-done-response', score=member.score), ephemeral=True)
        helper.AddCommand(change_score)


    if "change-member" not in disabled_commands or disabled_commands["change-member"]:
        @bot.slash_command(
            name=loc.GetString("change-member-stat-command-name"),
            description=loc.GetString("change-member-stat-command-description")
        )
        async def change_member_stat(
            inter: disnake.CommandInteraction,
            mem: disnake.Member = commands.Param(
                name=loc.GetString('change-member-stat-command-param-mem-name'),
                description=loc.GetString('change-member-stat-command-param-mem-description')
            ),
            param: str = commands.Param(
                name=loc.GetString('change-member-stat-command-param-param-name'),
                description=loc.GetString('change-member-stat-command-param-param-description'),
                choices=[
                    loc.GetString('change-member-stat-command-param-param-done-tasks'),
                    loc.GetString('change-member-stat-command-param-param-curation-tasks'),
                    loc.GetString('change-member-stat-command-param-param-notes'),
                    loc.GetString('change-member-stat-command-param-param-warns')
                ]
            ),
            project: str = commands.Param(
                name=loc.GetString('change-member-stat-command-param-project-name'),
                description=loc.GetString('change-member-stat-command-param-project-description'),
                choices=get_projects(),
                default=None
            ),
            mode: str = commands.Param(
                name=loc.GetString('change-member-stat-command-param-mode-name'),
                description=loc.GetString('change-member-stat-command-param-mode-description'),
                choices=[loc.GetString('add'), loc.GetString('remove')]
            ),
            value: str = commands.Param(
                name=loc.GetString('change-member-stat-command-param-value-name'),
                description=loc.GetString('change-member-stat-command-param-value-description')
            )):
            member = Member(mem)

            if param == loc.GetString('change-member-stat-command-param-param-done-tasks') and project:
                if project not in member.doneTasks:
                    member.doneTasks[project] = []

                if mode == loc.GetString('add'):
                    member.doneTasks[project].append(value)
                else:
                    member.doneTasks[project] = member.rem_from_stat(member.doneTasks[project], value)
            elif param == loc.GetString('change-member-stat-command-param-param-curation-tasks') and project:
                if project not in member.curationTasks:
                    member.curationTasks[project] = []

                if mode == loc.GetString('add'):
                    member.curationTasks[project].append(value)
                else:
                    member.curationTasks[project] = member.rem_from_stat(member.curationTasks[project], value)
            elif param == loc.GetString('change-member-stat-command-param-param-notes'):
                if mode == loc.GetString('add'):
                    member.notes.append(value)
                else:
                    member.notes = member.rem_from_stat(member.notes, value)
                    Logger.secret(inter, loc.GetString('change-member-stat-command-log-note-removed', value=value, name=mem.name))
            elif param == loc.GetString('change-member-stat-command-param-param-warns'):
                if mode == loc.GetString('add'):
                    member.warns.append(value)
                else:
                    member.warns = member.rem_from_stat(member.warns, value)
                    Logger.secret(inter, loc.GetString('change-member-stat-command-log-warn-removed', value=value, id=mem.id))

            member.update()
            await inter.send(content=loc.GetString('command-done-response'), ephemeral=True)
            Logger.medium(inter, loc.GetString('change-member-stat-command-log-stat-changed', name=mem.name, param=param))
        helper.AddCommand(change_member_stat)


    if "member-ckey" not in disabled_commands or disabled_commands["member-ckey"]:
        @bot.slash_command(
            name=loc.GetString("member-ckey-command-name"),
            description=loc.GetString("member-ckey-command-description")
        )
        async def member_ckey(
            inter: disnake.CommandInteraction,
            mem: disnake.Member = commands.Param(
                name=loc.GetString('member-ckey-command-param-mem-name'),
                description=loc.GetString('member-ckey-command-param-mem-description')
            ),
            ckey: str = commands.Param(
                name=loc.GetString('member-ckey-command-param-ckey-name'),
                description=loc.GetString('member-ckey-command-param-ckey-description')
            )):
            Member(mem).set_ckey(ckey)
            await inter.send(content=loc.GetString('command-done-response'), ephemeral=True)
            Logger.medium(inter, loc.GetString('member-ckey-command-log-ckey-set', name=mem.name, ckey=ckey))
        helper.AddCommand(member_ckey)

