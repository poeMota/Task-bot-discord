class EventSystem:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(EventSystem, cls).__new__(cls)
            cls.events = {}
        return cls.instance

    def register(self, event) -> bool:
        if event not in self.events:
            self.events[event] = []
            print(f"Registered {type(event).__name__} event")
            return True
        else:
            raise Exception("Event already registered")

    def subscribe_event(self, subscriber, event) -> bool:
        if event in self.events and subscriber not in self.events[event]:
            self.events[event].append(subscriber)
            return True
        else:
            raise Exception("Event not registered or subscriber already subscribed")

    def unsubscribe_event(self, subscriber, event) -> bool:
        if event in self.events and subscriber in self.events[event]:
            self.events[event].remove(subscriber)
            return True
        else:
            return False

    def unsubscribe_all(self, ent):
        methods = [getattr(ent, method_name) for method_name in dir(ent) if callable(getattr(ent, method_name))]
        for method in methods:
            for event in self.events:
                self.unsubscribe_event(method, event)

    def raise_event(self, event):
        if event in self.events:
            for subscriber in self.events[event]:
                print(f"{subscriber} take event")
                subscriber(ev=event)
            return True
        else:
            return False