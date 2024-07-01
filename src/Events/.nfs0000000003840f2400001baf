from src.EventManager import Event


class _OnMemberInfoChanged(Event):
    def __init__(self):
        super().__init__()
onMemberInfoChanged = _OnMemberInfoChanged()


class _OnMemberTaskLeave(Event):
    def __init__(self):
        super().__init__()
        self.task = None
onMemberTaskLeave = _OnMemberTaskLeave()