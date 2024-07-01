from src.EventManager.event_system import EventSystem

EventSystem = EventSystem()


class Event:
    def __init__(self):
        self.Raiser = None
        EventSystem.register(self)

    def update(self, raiser):
        self.Raiser = raiser

    def subscribe(self, subscriber):
        EventSystem.subscribe_event(subscriber, self)

    def raiseEvent(self, raiser):
        self.update(raiser)
        print(f"Raised {type(self).__name__} event")
        EventSystem.raise_event(self)
