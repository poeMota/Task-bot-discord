import os
from pathlib import Path

from src.Config import *


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
                self.CollectLocale(get_data_path() + path + '/' + filename)


    def GetString(self, message: str, **params) -> str:
        msg = self.locs_data[message]
        for param in params:
            if f"<{param}>" in msg:
                msg.replace(f"<{param}>", params[param])
        return msg

