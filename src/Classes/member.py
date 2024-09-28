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
            self.inTasks = {}
            self.doneTasks = {}
            self.curationTasks = {}
            self.ownFolder = ""
            self.score = 0
            self.AllTimeScore = 0

            self.ckey = ""
            self.warns = []
            self.notes = []
            self.last_activity = {}
            self.read_member_info()

            # Temp
            self.currentMagazinePage = 0
            self._initialized = True


    def read_member_info(self) -> None:
        members_data = json_read("members_database")

        if str(self.id) not in members_data:
            self.write_member_info()
            return

        self.inTasks, self.doneTasks, self.curationTasks, self.ownFolder, self.score, self.AllTimeScore, self.ckey, self.warns, self.notes = (
            {} if "в бригадах" not in members_data[str(self.id)] else members_data[str(self.id)]["в бригадах"],
            {} if "выполненные заказы" not in members_data[str(self.id)] else members_data[str(self.id)]["выполненные заказы"],
            {} if "курирование заказов" not in members_data[str(self.id)] else members_data[str(self.id)]["курирование заказов"],
            "" if "личная папка" not in members_data[str(self.id)] else members_data[str(self.id)]["личная папка"],
            0 if "очки" not in members_data[str(self.id)] else members_data[str(self.id)]["очки"],
            0 if "очков за всё время" not in members_data[str(self.id)] else members_data[str(self.id)]["очков за всё время"],
            "" if "@сикей" not in members_data[str(self.id)] else members_data[str(self.id)]["@сикей"],
            [] if "@предупреждения" not in members_data[str(self.id)] else members_data[str(self.id)]["@предупреждения"],
            [] if "@заметки" not in members_data[str(self.id)] else members_data[str(self.id)]["@заметки"]
        )

        if "@последняя активность" in members_data[str(self.id)] and members_data[str(self.id)]["@последняя активность"]:
            self.last_activity = members_data[str(self.id)]["@последняя активность"]
        else: self.last_activity = {}


    def write_member_info(self):
        members_data = json_read("members_database")

        inTasks = {}
        for projectName in self.inTasks:
            inTasks[projectName] = []
            for task in self.inTasks[projectName]:
                if isinstance(task, str): inTasks[projectName].append(task)
                else: inTasks[projectName].append(task.url)

        members_data[str(self.id)] = {
            "в бригадах": inTasks,
            "выполненные заказы": self.doneTasks,
            "курирование заказов": self.curationTasks,
            "личная папка": self.ownFolder,
            "очки": self.score,
            "очков за всё время": self.AllTimeScore,
            "@сикей": self.ckey,
            "@последняя активность": self.last_activity,
            "@предупреждения": self.warns,
            "@заметки": self.notes
        }
        json_write("members_database", members_data)


    def update(self):
        self.write_member_info()


    def in_tasks(self, project) -> int:
        if project.name not in self.inTasks:
            return 0
        return len(self.inTasks[project.name])


    def join_task(self, task):
        projectName = task.project.name
        if projectName not in self.inTasks:
            self.inTasks[projectName] = []

        if task.url not in self.inTasks[projectName]:
            self.inTasks[projectName].append(task.url)
            self.update()
            task.on_join(self)
            Logger.debug(f"{self.member.display_name} присоединился к заказу {task.name}")
            Events.onMemberInfoChanged.raiseEvent(self)


    def leave_task(self, task):
        projectName = task.project.name
        if projectName not in self.inTasks:
            return

        if task.url in self.inTasks[projectName]:
            self.inTasks[projectName].remove(task.url)
            self.update()
            task.on_leave(self)
            Logger.debug(f"{self.member.display_name} покинул заказ {task.name}")
            Events.onMemberInfoChanged.raiseEvent(self)


    def task_end(self, task):
        # Change score
        self.change_score(task._endingResult[self], True)
        if task._endingResult[self] > 0:
            if task.brigadire != self:
                if task.project.name not in self.doneTasks:
                    self.doneTasks[task.project.name] = []
                self.doneTasks[task.project.name].append(task.get_string())
                Logger.debug(f"заказ {task.name} записан в выполенные заказы пользователя {self.member.display_name}")
            else:
                if task.project.name not in self.curationTasks:
                    self.curationTasks[task.project.name] = []
                self.curationTasks[task.project.name].append(task.get_string())
                Logger.debug(f"заказ {task.name} записан в курирование заказов пользователя {self.member.display_name}")
            if task.project.name not in self.last_activity:
                self.last_activity[task.project.name] = []
            self.last_activity[task.project.name] = datetime.now().strftime("%Y-%m-%d")

        self.leave_task(task)
        self.update()


    def get_info(self) -> dict:
        members_data = json_read("members_database")
        return members_data[str(self.id)]


    def stat_embed(self, showHidden = False) -> disnake.Embed:
        return embed_from_dict(
            title=f"Статистика {self.member.name}",
            description=None,
            color=self.member.roles[-1].color,
            D=self.get_info(),
            showHidden=showHidden
        )


    def inactivity_days(self, project):
        try:
            return (datetime.now() - datetime.strptime(self.last_activity[project.name], "%Y-%m-%d")).days
        except:
            return "неизвестно"


    def stat_post_text(self, project) -> str:
        show_data = {
            "очки": self.score
            }
        text = (f"╠︎ **заказов вып.:** {0 if project.name not in self.doneTasks else len(self.doneTasks[project.name])}\n" +
                f"╠︎ **курирование:** {0 if project.name not in self.curationTasks else len(self.curationTasks[project.name])}\n" +
                f"╠︎ **в бригадах:** {self.in_brigades_text(project)}\n" +
                f"╠︎ **активность:** {self.inactivity_days(project)} дней назад")

        for key in show_data:
            char = "╠︎"
            if show_data[key] == list(show_data.values())[-1]: char = "╚"
            text = f"{text}\n**{char} {key}**: {show_data[key]}"

        return text


    def in_brigades_text(self, project):
        text = ""
        if project.name not in self.inTasks:
            return "нет"

        for task in self.inTasks[project.name]:
            if isinstance(task, str):
                text = f"{text}\n- {task}"
            else: text = f"{text}\n- {task.url}"

        if not text: text = "нет"
        return text


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


    def set_ckey(self, ckey):
        self.ckey = ckey
        self.update()


    def rem_from_stat(self, param, value):
        if type(param) is list:
            for i in list(param):
                if value in i:
                    param.remove(i)
        elif type(param) is dict:
            for key in dict(param):
                if key == value or param[key] == value:
                    del param[key]
                elif type(param[key]) is list:
                    for i in param[key]:
                        if value in i:
                            param[key].remove(i)
        return param


    def __del__(self):
        self.write_member_info()

