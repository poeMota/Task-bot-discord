import disnake
from disnake import utils

from src.Logger import Logger
from src.Classes import Member
from src.Localization import LocalizationManager

loc = LocalizationManager()

class Page:
    def __init__(self, inter: disnake.AppCommandInteraction, proto, replacements):
        self.name = None
        self.description = None
        self.price = 0
        self.onBuy = []
        self.access = ["everyone"]
        self.notAccess = []

        self.replacements = {
            "<AuthorPing>": f"<@{inter.author.id}>",
            "<!NotifiThread>": Logger.secretLogThread,
            "<!LogChannel>": Logger.logChannel,
            "\\n": "\n"
        }
        if replacements:
            for repl in replacements:
                self.replacements[f"<{repl}>"] = replacements[repl]

        self.readProto(proto)


    def readProto(self, proto: dict):
        if not "type" in proto or not proto["type"] == "page":
            raise ValueError("Given non page proto")

        [setattr(self, arg, self.convertStr(loc.GetString(proto[arg])) if type(proto[arg]) is str
                                                                       else proto[arg])
        for arg in proto if arg in dir(self)]


    def convertStr(self, string: str):
        string = string.removeprefix('"').removesuffix('"')

        for replacement in self.replacements:
            if replacement in string:
                if replacement.startswith('<!'):
                    return self.replacements[replacement]
                else:
                    string = string.replace(replacement, self.replacements[replacement])
        return string


    def isAccess(self, member: disnake.Member):
        access = False

        if "everyone" in self.access:
            access = True

        for role in member.roles:
            if role.name.lower() in self.access:
                access = True
            if role.name.lower() in self.notAccess:
                access = False
                break

        return access


    async def buy(self, inter: disnake.AppCommandInteraction):
        member = Member(inter.author)
        if member.score >= self.price:
            member.change_score(-self.price, False)
            for i in self.onBuy:
                for name in i:
                    method = getattr(self, name)
                    await method(inter=inter, **i[name])
            Logger.medium(inter, f"{inter.author.display_name} совершил покупку **{self.name}**")


    async def giveRoles(self, inter: disnake.AppCommandInteraction, roles: list[str]):
        _roles = [role.lower() for role in roles]

        for role in inter.guild.roles:
            if role.name.lower() in _roles:
                await inter.author.add_roles(role)


    async def removeRoles(self, inter: disnake.AppCommandInteraction, roles: list[str]):
        _roles = [role.lower() for role in roles]

        for role in inter.guild.roles:
            if role.name.lower() in _roles:
                await inter.author.remove_roles(role)


    async def sendMessage(self, inter: disnake.AppCommandInteraction, message: str, channel: str | int = None):
        message = self.convertStr(message)

        if channel:
            if type(channel) is str:
                channel: disnake.TextChannel = self.convertStr(channel)
            if type(channel) is int:
                channel = utils.get(inter.guild.channels, id=channel)

            await channel.send(content=message)
        else:
            await inter.channel.send(content=message)


    async def mute(self, inter: disnake.AppCommandInteraction, member: int | str, duration: int):
        if member is str:
            member = self.convertStr(member)
        if member is int:
            member = utils.get(inter.guild.members, id=member)

        if member:
            await member.timeout(duration=duration)


    async def changeScore(self, inter: disnake.AppCommandInteraction, member: int | str, score: int):
        if member is str:
            member = self.convertStr(member)
        if member is int:
            member = utils.get(inter.guild.members, id=member)

        if member is disnake.Member:
            Member(member).change_score(score)

