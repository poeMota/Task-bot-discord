import disnake

from src.Logger import Logger
from src.Classes import Member


class Page:
    def __init__(self, inter: disnake.AppCommandInteraction, proto):
        self.name = None
        self.description = None
        self.price = 0
        self.onBuy = []
        self.access = ["everyone"]
        self.notAccess = []

        self.replacements = {
            "<HeadMapperPing>": "<@&1181535312304951296>",
            "<MotaPing>": "<@1046425922200420505>",
            "<AuthorPing>": f"<@{inter.author.id}>",
            "<!NotifiThread>": Logger.secretLogThread,
            "\\n": "\n"
        }

        self.readProto(proto)
    

    def readProto(self, proto: dict):
        if not "type" in proto or not proto["type"] == "page":
            raise ValueError("Given non page proto")

        [setattr(self, 
                 arg, 
                 self.convertStr(proto[arg])
                    if type(proto[arg]) is str
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


    async def sendMessage(self, inter: disnake.AppCommandInteraction, message: str, channel: str = None):
        message = self.convertStr(message)

        if channel: 
            channel: disnake.TextChannel = self.convertStr(channel)
            await channel.send(content=message)
        else:
            await inter.channel.send(content=message)