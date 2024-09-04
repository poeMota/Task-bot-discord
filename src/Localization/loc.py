import os
from pathlib import Path

from src.Config import *
from src.Logger import *


class LocalizationManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocalizationManager, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance


    def __init__(self):
        if not self._initialized:
            self.locs_data = {}
            self.culture = "EN_us"

            self.CollectLocale()
            self._initialized = True
    

    def CollectLocale(self):
        config = from_toml("config", "Localization")

        self.locs_data = {}
        self.culture = config["culture"]

        self._collectLocale(config["locale_path"] + '/' + self.culture)


    def _collectLocale(self, path):
        for filename in os.listdir(get_data_path() + path):
            if Path(get_data_path() + path + '/' + filename).is_file():
                self.locs_data.update(yaml_read(path + '/' + filename.split('.')[0]))
            else:
                self._collectLocale(path + '/' + filename)


    def GetString(self, message: str, **params) -> str:
        if message not in self.locs_data:
            Logger.tofile(f"unknown loc string {message}", Levels.Error)
            return message

        msg: str = self.locs_data[message]
        for param in params:
            _param = '{' + param + '}'
            if _param in msg:
                msg = msg.replace(_param, str(params[param]))
            else:
                Logger.tofile(f"unknown param {param} for loc string {msg}", Levels.Error)
        return msg

