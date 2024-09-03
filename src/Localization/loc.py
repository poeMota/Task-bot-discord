import os
from pathlib import Path

from src.Config import *
from src.Logger import *

from pprint import pprint

class LocalizationManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocalizationManager, cls).__new__(cls)
            config = from_toml("config", "Localization")
            cls.culture = config["culture"]
            cls.locs_data = {}

            cls.CollectLocale(cls, config["locale_path"])
        return cls.instance


    def CollectLocale(self, path):
        for filename in os.listdir(get_data_path() + path):
            if Path(get_data_path() + path + '/' + filename).is_file():
                self.locs_data.update(from_yaml(path + '/' + filename.split('.')[0], self.culture))
            else:
                self.CollectLocale(self, path + '/' + filename)


    def GetString(self, message: str, **params) -> str:
        if message not in self.locs_data:
            Logger.tofile(f"unknown loc string {message}")
            return message

        msg = self.locs_data[message]
        for param in params:
            if '{' + param + '}' in msg:
                msg.replace('{' + param + '}', params[param])
            else:
                Logger.tofile(f"unknown param {param} for loc string {msg}", Levels.Error)
        return msg

