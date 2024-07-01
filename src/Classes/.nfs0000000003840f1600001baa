import disnake
import enum

from src.EventManager import Event
from src.Config import *
import src.Events as Events

class Tag:
    _instances = {}

    def __new__(cls, tag: disnake.ForumTag, project, *args, **kwargs):
        if tag.id in cls._instances:
            return cls._instances[tag.id]
        instance = super().__new__(cls)
        cls._instances[tag.id] = instance
        return instance


    def __init__(self, tag: disnake.ForumTag, project) -> None:
        if not hasattr(self, '_initialized'):
            self.tag = tag
            self.id = tag.id
            self.project = project

            self.tagType = TagTypes.inWork
            self.ping: disnake.Role = 0
            self.scoreModifier = 0
            self.maxMembers = 0

            self.read_tag()
            
            self._initialized = True


    def __str__(self) -> str:
        if self.tagType is TagTypes.difficult:
            return f"**тег**: {self.tag.emoji}{self.tag.name}\nㅤ**тип**: {self.tagType}\nㅤ**очки**: {self.scoreModifier}\nㅤ**задаёт макс. членов**: {self.maxMembers}"
        elif self.tagType is TagTypes.ping:
            return f"**тег**: {self.tag.emoji}{self.tag.name}\nㅤ**тип**: {self.tagType}\nㅤ**пингует**: {self.ping.id}"
        else:
            return f"**тег**: {self.tag.emoji}{self.tag.name}\nㅤ**тип**: {self.tagType}"


    def __repr__(self) -> str:
        return f"{self.tagType} tag of project {self.project.name}"


    def read_tag(self):
        project_data = json_read("projects")

        if str(self.id) not in project_data[self.project.name]["tags"]:
            self.write_tag()
            return

        tag = project_data[self.project.name]["tags"][str(self.id)]

        if tag["type"] == "ping_tag": 
            self.tagType = TagTypes.ping
            self.ping = None if "ping_role" not in tag else self.project.bot.get_role(tag["ping_role"])
        elif tag["type"] == "difficult_tag": 
            self.tagType = TagTypes.difficult
            self.scoreModifier = 0 if "score_modifier" not in tag else tag["score_modifier"]
            self.maxMembers = 20 if "max_members" not in tag else tag["max_members"]
        elif tag["type"] == "in_work_tag": self.tagType = TagTypes.inWork
        elif tag["type"] == "frozen_tag": self.tagType = TagTypes.frozen
        elif tag["type"] == "ended_tag": self.tagType = TagTypes.end
        elif tag["type"] == "closed_tag": self.tagType = TagTypes.closed


    def write_tag(self):
        project_data = json_read("projects")

        tag = {
            "type": self.tagType.value,
        }
        if self.tagType == TagTypes.difficult: 
            tag["score_modifier"] = self.scoreModifier
            tag["max_members"] = self.maxMembers
        elif self.tagType == TagTypes.ping: 
            tag["ping_role"] = self.ping.id

        project_data[self.project.name]["tags"][str(self.id)] = tag
        json_write("projects", project_data)


class TagTypes(enum.Enum):
    ping = "ping_tag"
    difficult = "difficult_tag"
    inWork = "in_work_tag"
    frozen = "frozen_tag"
    end = "ended_tag"
    closed = "closed_tag"