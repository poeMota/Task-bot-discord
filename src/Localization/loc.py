import os
from pathlib import Path

from src.Config import *
from src.Logger import *


class LocalizationManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocalizationManager, cls).__new__(cls)
            config = from_toml("config", "Localization")
            cls.culture = config["culture"]
            cls.locs_data = {}

            cls.CollectLocale(cls, config["locale_path"] + '/' + cls.culture)
        return cls.instance


    def CollectLocale(self, path):
        for filename in os.listdir(get_data_path() + path):
            if Path(get_data_path() + path + '/' + filename).is_file():
                self.locs_data.update(yaml_read(path + '/' + filename.split('.')[0]))
            else:
                self.CollectLocale(self, path + '/' + filename)


    def GetString(self, message: str, **params) -> str:
        if message not in self.locs_data:
            Logger.tofile(f"unknown loc string {message}")
            return message

        msg: str = self.locs_data[message]
        for param in params:
            _param = '{' + param + '}'
            print(_param, msg)
            if _param in msg:
                msg = msg.replace(_param, str(params[param]))
            else:
                Logger.tofile(f"unknown param {param} for loc string {msg}", Levels.Error)
        return msg

