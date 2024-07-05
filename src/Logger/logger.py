from datetime import datetime
import enum
import asyncio
import disnake


class Levels(enum.Enum):
    High = "**[High]**"
    Medium = "**[Medium]**"
    Low = "[Low]"
    Debug = "[Debug]"
    Secret = "**[Оповещение]**"


class Logger:
    logChannel: disnake.TextChannel = None
    secretLogThread: disnake.Thread = None

    @staticmethod
    def log(level: Levels, text: str, channel: disnake.TextChannel | disnake.Thread, inter: disnake.AppCommandInteraction = None):
        if not isinstance(channel, (disnake.TextChannel, disnake.Thread)):
            return

        loop = asyncio.get_event_loop()
        if inter is not None:
            loop.create_task(channel.send(f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <{inter.author.name}>: {text}"))
        else:
            loop.create_task(channel.send(f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <система>: {text}"))

    @staticmethod
    def low(inter, text: str):
        Logger.log(Levels.Low, text, Logger.logChannel, inter)

    @staticmethod
    def medium(inter, text: str):
        Logger.log(Levels.Medium, text, Logger.logChannel, inter)

    @staticmethod
    def high(inter, text: str):
        Logger.log(Levels.High, text, Logger.logChannel, inter)

    @staticmethod
    def debug(text: str):
        Logger.log(Levels.Debug, text, Logger.logChannel)

    @staticmethod
    def secret(inter, text: str):
        Logger.log(Levels.Secret, text, Logger.secretLogThread, inter)