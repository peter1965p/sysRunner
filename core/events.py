class EventBus:
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        self.listeners.setdefault(event, []).append(callback)

    def emit(self, event, payload=None):
        for cb in self.listeners.get(event, []):
            cb(payload)
