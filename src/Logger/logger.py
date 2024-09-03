from datetime import datetime
import enum
import asyncio
import disnake
import os
from pathlib import Path

from src.Config import get_data_path


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
            _text = f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <{inter.author.name}>: {text}"
        else:
            _text = f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <система>: {text}"
        loop.create_task(channel.send(_text))
        Logger.tofile(_text.replace('**', ''), prefix=False)

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

    @staticmethod
    def tofile(text: str, level: Levels = Levels.Debug, prefix: bool = True):
        if not Path(get_data_path() + "logs").is_dir():
            os.mkdir(get_data_path() + "logs")
        with open(get_data_path() + f"logs/{datetime.now().strftime("%Y-%m-%d")}-log.txt", 'a', encoding="utf8") as f:
            _text = f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <система>: {text}\n" if prefix else f'{text}\n'
            f.write(_text)
            print(_text)

