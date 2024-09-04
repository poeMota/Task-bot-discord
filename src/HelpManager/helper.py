import inspect
import disnake

import disnake.ext
from disnake.ext.commands import InvokableSlashCommand
from src.Localization import LocalizationManager

loc = LocalizationManager()

class HelpManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(HelpManager, cls).__new__(cls)
            cls.commands = []
        return cls.instance
    

    def AddCommand(self, command):
        if command not in self.commands:
            self.commands.append(command)
    

    def AddCommands(self, commands: list):
        [self.AddCommand(command) for command in commands]


    def GetCommandHelp(self, command: InvokableSlashCommand) -> disnake.Embed:
        command_str = command.callback.__name__.replace('_', '-')
        description = f'**Описание**: {loc.GetString(f"{command_str}-command-description")}\n'
        remark = f"{command_str}-command-remark"
        if remark != loc.GetString(remark):
            description = f"{description}**Примечание**: {loc.GetString(remark)}\n"

        embed_width = 34
        embed = disnake.Embed(
            title=loc.GetString(f"{command_str}-command-name"),
            description=description + "ㅤ" * embed_width,
            color=disnake.Color.orange()
        )

        params = inspect.signature(command.callback).parameters
        for param_name, param in params.items():
            if param.default is not inspect._empty:
                param_name = param_name.lower().replace('_', '')
                value = f'- **Описание**: {loc.GetString(f"{command_str}-command-param-{param_name}-description")}'
                
                remark = f"{command_str}-command-param-{param_name}-remark"
                if remark != loc.GetString(remark):
                    value = f"{value}\n- **Примечание**: {loc.GetString(remark)}"

                embed.add_field(
                    name=loc.GetString(f"{command_str}-command-param-{param_name}-name"),
                    value=value,
                    inline=False
                )
        return embed
    

    def GetCommandsHelp(self):
        return [self.GetCommandHelp(command) for command in self.commands]