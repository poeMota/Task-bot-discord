from datetime import datetime
import enum
import asyncio
import disnake
import os
import sys
from pathlib import Path

from src.Config import *


class Levels(enum.Enum):
    High = "**[High]**"
    Medium = "**[Medium]**"
    Low = "[Low]"
    Debug = "[Debug]"
    Secret = "**[Оповещение]**"
    Error = "[Error]"


class Logger:
    logChannel: disnake.TextChannel = None
    secretLogThread: disnake.Thread = None

    config = from_toml("config", "Logging")
    if not config: config = {}

    @staticmethod
    def log(level: Levels, text: str, channel: disnake.TextChannel | disnake.Thread, inter: disnake.AppCommandInteraction = None):
        if inter is not None:
            _text = f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <{inter.author.name}>: {text}"
        else:
            _text = f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <система>: {text}"

        Logger.tofile(_text.replace('**', ''), prefix=False)

        if not isinstance(channel, (disnake.TextChannel, disnake.Thread)):
            return
        loop = asyncio.get_event_loop()
        loop.create_task(channel.send(_text))

    @staticmethod
    def low(inter, text: str):
        if "low" not in Logger.config or Logger.config["low"]:
            Logger.log(Levels.Low, text, Logger.logChannel, inter)

    @staticmethod
    def medium(inter, text: str):
        if "medium" not in Logger.config or Logger.config["medium"]:
            Logger.log(Levels.Medium, text, Logger.logChannel, inter)

    @staticmethod
    def high(inter, text: str):
        if "high" not in Logger.config or Logger.config["high"]:
            Logger.log(Levels.High, text, Logger.logChannel, inter)

    @staticmethod
    def debug(text: str):
        if "debug" not in Logger.config or Logger.config["debug"]:
            Logger.log(Levels.Debug, text, Logger.logChannel)

    @staticmethod
    def error(text: str):
        if "error" not in Logger.config or Logger.config["error"]:
            Logger.log(Levels.Error, text, Logger.logChannel)

    @staticmethod
    def secret(inter, text: str):
        if "secret" not in Logger.config or Logger.config["error"]:
            Logger.log(Levels.Secret, text, Logger.secretLogThread, inter)

    @staticmethod
    def tofile(text: str, level: Levels = Levels.Debug, prefix: bool = True):
        if not Path(get_data_path() / "logs").is_dir():
            os.mkdir(get_data_path() / "logs")
        with open(get_data_path() / f"logs/{datetime.now().strftime("%Y-%m-%d")}-log.txt", 'a', encoding="utf8") as f:
            _text = f"{level.value} ({datetime.now().strftime("%Y-%m-%d %H:%M")}) <система>: {text}\n" if prefix else f'{text}\n'
            _text = _text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            f.write(_text)
            print(_text, end="")

