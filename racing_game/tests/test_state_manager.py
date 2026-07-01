import pytest
from src.core.state_manager import StateManager


class DummyState:
    def __init__(self):
        self.entered = False
        self.exited = False
        self.events = None
        self.last_dt = None
        self.screen = None
    def enter(self):
        self.entered = True
    def exit(self):
        self.exited = True
    def handle_events(self, events):
        self.events = events
    def update(self, dt):
        self.last_dt = dt
    def render(self, screen):
        self.screen = screen


class TestStateManager:
    """RED: escribo test para StateManager que aún no existe.
       GREEN: al implementar StateManager, todos pasan.
       REFACTOR: se podría validar que change_state con name inválido no crashee.
    """

    @staticmethod
    def _make_dummy():
        return DummyState()

    @pytest.fixture
    def manager(self):
        return StateManager()

    @pytest.fixture
    def dummy_state(self):
        return DummyState()

    def test_add_state(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        assert "test" in manager.states

    def test_change_state_sets_current(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        manager.change_state("test")
        assert manager.current_state is dummy_state

    def test_change_state_calls_enter(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        manager.change_state("test")
        assert dummy_state.entered is True

    def test_change_state_calls_exit_on_current(self, manager, dummy_state):
        state_b = self._make_dummy()
        manager.add_state("a", dummy_state)
        manager.add_state("b", state_b)
        manager.change_state("a")
        manager.change_state("b")
        assert dummy_state.exited is True

    def test_change_state_with_enter_false(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        manager.change_state("test", enter=False)
        assert dummy_state.entered is False

    def test_change_state_nonexistent(self, manager):
        manager.change_state("ghost")
        assert manager.current_state is None

    def test_handle_events_delegates(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        manager.change_state("test")
        manager.handle_events([1, 2, 3])
        assert dummy_state.events == [1, 2, 3]

    def test_update_delegates(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        manager.change_state("test")
        manager.update(0.016)
        assert dummy_state.last_dt == 0.016

    def test_render_delegates(self, manager, dummy_state):
        manager.add_state("test", dummy_state)
        manager.change_state("test")
        manager.render("screen")
        assert dummy_state.screen == "screen"

    def test_methods_safe_when_no_state(self, manager):
        manager.handle_events([])
        manager.update(0.016)
        manager.render("screen")

    def test_add_multiple_states(self, manager, dummy_state):
        state_b = self._make_dummy()
        manager.add_state("a", dummy_state)
        manager.add_state("b", state_b)
        manager.change_state("a")
        assert manager.current_state is dummy_state
        manager.change_state("b")
        assert manager.current_state is state_b
