from datetime import datetime
import enum
import asyncio
import disnake


class Levels(enum.Enum):
    High = "**[High]**"
    Medium = "**[Medium]**"
    Low = "[Low]"
    Debug = "[Debug]"


class Logger:
    logChannel: disnake.TextChannel = None

    @staticmethod
    def log(level: Levels, text: str, inter: disnake.AppCommandInteraction = None):
        loop = asyncio.get_event_loop()
        if inter is not None:
            loop.create_task(Logger.logChannel.send(f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <{inter.author.name}>: {text}"))
        else:
            loop.create_task(Logger.logChannel.send(f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <система>: {text}"))

    @staticmethod
    def low(inter, text: str):
        Logger.log(Levels.Low, text, inter)

    @staticmethod
    def medium(inter, text: str):
        Logger.log(Levels.Medium, text, inter)

    @staticmethod
    def high(inter, text: str):
        Logger.log(Levels.High, text, inter)

    @staticmethod
    def debug(text: str):
        Logger.log(Levels.Debug, text)