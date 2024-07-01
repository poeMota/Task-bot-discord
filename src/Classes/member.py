from datetime import datetime
import disnake

from src.Logger import *
from src.Config import *
from src.Tools import embed_from_dict

import src.Events as Events

class Member:
    _instances = {}

    def __new__(cls, member: disnake.Member, *args, **kwargs):
        if member.id in cls._instances:
            return cls._instances[member.id]
        instance = super().__new__(cls)
        cls._instances[member.id] = instance
        return instance


    def __init__(self, member: disnake.Member) -> None:
        if not hasattr(self, '_initialized'):
            self.member: disnake.Member = member
            # Write/Read from config
            self.id = self.member.id
            self.rank = self.member.roles[-1].name
            self.inTasks = []
            self.doneTasks = []
            self.curationTasks = []
            self.ownFolder = ""
            self.score = 0
            self.AllTimeScore = 0

            self.warns = []
            self.notes = []
            self.last_activity = ""
            self.read_member_info()

            # Temp
            self.currentMagazinePage = 0
            self._initialized = True


    def read_member_info(self) -> None:
        members_data = json_read("members_database")

        if str(self.id) not in members_data:
            self.write_member_info()
            return

        self.inTasks, self.doneTasks, self.curationTasks, self.ownFolder, self.score, self.AllTimeScore, self.warns, self.notes = (
            "" if "в бригадах" not in members_data[str(self.id)] else members_data[str(self.id)]["в бригадах"],
            [] if "выполненные заказы" not in members_data[str(self.id)] else members_data[str(self.id)]["выполненные заказы"],
            [] if "курирование заказов" not in members_data[str(self.id)] else members_data[str(self.id)]["курирование заказов"],
            "" if "личная папка" not in members_data[str(self.id)] else members_data[str(self.id)]["личная папка"],
            0 if "очки" not in members_data[str(self.id)] else members_data[str(self.id)]["очки"],
            0 if "очков за всё время" not in members_data[str(self.id)] else members_data[str(self.id)]["очков за всё время"],
            [] if "@предупреждения" not in members_data[str(self.id)] else members_data[str(self.id)]["@предупреждения"],
            [] if "@заметки" not in members_data[str(self.id)] else members_data[str(self.id)]["@заметки"]
        )

        if "@последняя активность" in members_data[str(self.id)] and members_data[str(self.id)]["@последняя активность"] != "":
            self.last_activity = members_data[str(self.id)]["@последняя активность"]
        else: self.last_activity = self._last_activity()


    def write_member_info(self):
        members_data = json_read("members_database")

        inTasks = []
        for task in self.inTasks:
            if isinstance(task, str): inTasks.append(task)
            else: inTasks.append(task.url)

        members_data[str(self.id)] = {
            "в бригадах": inTasks,
            "выполненные заказы": self.doneTasks,
            "курирование заказов": self.curationTasks,
            "личная папка": self.ownFolder,
            "очки": self.score,
            "очков за всё время": self.AllTimeScore,
            "@последняя активность": self.last_activity,
            "@предупреждения": self.warns,
            "@заметки": self.notes
        }
        json_write("members_database", members_data)


    def update(self):
        self.write_member_info()


    def join_task(self, task):
        self.inTasks.append(task)
        self.update()
        task.on_join(self)
        Logger.debug(f"{self.member.display_name} присоединился к заказу {task.name}")
        Events.onMemberInfoChanged.raiseEvent(self)


    def leave_task(self, task):
        self.inTasks.remove(task)
        self.update()
        task.on_leave(self)
        Logger.debug(f"{self.member.display_name} покинул заказ {task.name}")
        Events.onMemberInfoChanged.raiseEvent(self)


    def task_end(self, task):
        # Change score
        self.change_score(task._endingResult[self], True)
        if task._endingResult[self] > 0:
            if task.brigadire != self:
                self.doneTasks.append(task.get_string())
                Logger.debug(f"заказ {task.name} записан в выполенные заказы пользователя {self.member.display_name}")
            else:
                self.curationTasks.append(task.get_string())
                Logger.debug(f"заказ {task.name} записан в курирование заказов пользователя {self.member.display_name}")
            self.last_activity = datetime.now().strftime("%Y-%m-%d")

        self.leave_task(task)
        self.update()


    def get_info(self) -> dict:
        members_data = json_read("members_database")
        return members_data[str(self.id)]
    

    def stat_embed(self, showHidden: False) -> disnake.Embed:
        return embed_from_dict(
            title=f"Статистика {self.member.name}",
            description=None,
            color=self.member.roles[-1].color,
            D=self.get_info(),
            showHidden= showHidden
        )
    

    def stat_post_text(self) -> str:
        show_data = {
            "очки": self.score
            }
        text = (f"╠︎ **заказов выполененно**: {len(self.doneTasks)}\n" +
                f"╠︎ **курирование заказов**: {len(self.curationTasks)}\n" +
                f"╠︎ **в бригадах**: {self.in_brigades_text()}\n" +
                f"╠︎ **последняя активность**: {self.last_activity}")

        for key in show_data:
            char = "╠︎"
            if show_data[key] == list(show_data.values())[-1]: char = "╚"
            text = f"{text}\n**{char} {key}**: {show_data[key]}"

        return text


    def in_brigades_text(self):
        text = ""
        for task in self.inTasks:
            if isinstance(task, str):
                text = f"{text} {task}"
            else: text = f"{text} {task.url}"

        if text == "": text = "нет"
        return text


    def _last_activity(self):
        format = "%Y-%m-%d"
        last_curation, last_task = None, None
        try:
            last_curation = datetime.strptime(self.curationTasks[-1].split(" ")[-1], format)
        except: last_curation = "неизвестно"

        try:
            last_task = datetime.strftime(datetime.strptime(self.doneTasks[-1].split(" ")[-1], format))
        except: last_task = "неизвестно"

        '''
        if last_curation == "неизвестно" and last_curation == "неизвестно":
            return "неизвестно"
        elif last_task != "неизвестно" and last_curation != "неизвестно":
            if last_curation > last_task: return datetime.strftime(last_curation, format)
            else: return datetime.strftime(last_task, format)
        elif last_curation == "неизвестно": return last_task
        else: return last_curation'''
        return last_task


    def change_score(self, score: int, allScore: bool = False) -> None:
        self.score += score
        if allScore: self.AllTimeScore += score
        self.update()
        Logger.debug(f"изменены очки пользователя {self.member.display_name} на {score}, allScore: {allScore}")
        Events.onMemberInfoChanged.raiseEvent(self)
    

    def folder_is_empty(self):
        return self.ownFolder.replace(" ", "") == ""


    def change_folder(self, folder: str):
        self.ownFolder = folder
        self.update()


    def rem_from_stat(self, param, value):
        for i in list(param):
            if value in i:
                param.remove(i)
        return param


    def __del__(self):
        self.write_member_info()