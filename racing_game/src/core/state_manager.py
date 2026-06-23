class StateManager:
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, name, state):
        self.states[name] = state

    def change_state(self, name, enter=True):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states.get(name)
        if self.current_state and enter:
            self.current_state.enter()

    def handle_events(self, events):
        if self.current_state:
            self.current_state.handle_events(events)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def render(self, screen):
        if self.current_state:
            self.current_state.render(screen)
