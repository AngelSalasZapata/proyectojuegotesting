import math
import pytest
from unittest.mock import MagicMock, patch

from settings import LAP_COUNT


class TestRaceLogic:
    """RED: tests de lógica de carrera (vueltas, fin de carrera).
       GREEN: implementar en _update_race_progress y _check_race_finish.
    """

    @pytest.fixture
    def mock_track(self):
        track = MagicMock()
        track.waypoints = [(100, 100), (300, 100), (400, 300), (300, 500),
                           (100, 500), (0, 300)]
        track.n = 6
        track.get_progress.return_value = 0.0
        track.check_lap.return_value = False
        return track

    @pytest.fixture
    def race_state(self, mock_track):
        from src.states.race_state import RaceState
        from src.core.state_manager import StateManager

        sm = StateManager()
        state = RaceState(sm)
        state.track = mock_track
        state.race_finished = False
        state.finish_order = []
        state.player = MagicMock()
        state.player.x = 200
        state.player.y = 200
        state.player.lap = 0
        state.player.finished = False
        state.player.segments_visited = set()
        return state

    def test_update_race_progress_gets_progress(self, race_state, mock_track):
        race_state._update_race_progress(race_state.player)
        assert mock_track.get_progress.called

    def test_lap_incremented_on_wrap(self, race_state, mock_track):
        race_state.player.last_progress = 5.0
        race_state.player.segments_visited = {0, 1, 2, 3, 4, 5}
        mock_track.get_progress.return_value = 0.5
        mock_track.check_lap.return_value = True
        race_state._update_race_progress(race_state.player)
        assert race_state.player.lap == 1

    def test_lap_not_incremented_without_enough_segments(self, race_state, mock_track):
        race_state.player.last_progress = 5.0
        race_state.player.segments_visited = {0, 1}
        mock_track.get_progress.return_value = 0.5
        mock_track.check_lap.return_value = True
        race_state._update_race_progress(race_state.player)
        assert race_state.player.lap == 0

    def test_car_finishes_at_lap_count(self, race_state, mock_track):
        race_state.player.lap = LAP_COUNT - 1
        race_state.player.last_progress = 5.0
        race_state.player.segments_visited = {0, 1, 2, 3, 4, 5}
        mock_track.get_progress.return_value = 0.5
        mock_track.check_lap.return_value = True
        race_state._update_race_progress(race_state.player)
        assert race_state.player.finished is True

    def test_finish_order_recorded(self, race_state, mock_track):
        race_state.player.lap = LAP_COUNT - 1
        race_state.player.last_progress = 5.0
        race_state.player.segments_visited = {0, 1, 2, 3, 4, 5}
        mock_track.get_progress.return_value = 0.5
        mock_track.check_lap.return_value = True
        race_state._update_race_progress(race_state.player)
        assert len(race_state.finish_order) > 0

    def test_segments_visited_tracked(self, race_state, mock_track):
        mock_track.get_progress.return_value = 2.3
        mock_track.check_lap.return_value = False
        race_state._update_race_progress(race_state.player)
        assert 2 in race_state.player.segments_visited

    def test_check_race_finish_not_triggered_early(self, race_state):
        race_state.player.finished = False
        race_state._check_race_finish()
        assert race_state.race_finished is False

    def test_player_position_in_results(self, race_state):
        from src.entities.car import Car
        race_state.player = Car(200, 200)
        race_state.player.finished = True
        race_state.player.lap = LAP_COUNT
        race_state.player.last_progress = 0.0
        race_state.finish_order = [("Jugador", 6, True, 90.0)]
        assert race_state.finish_order[0][0] == "Jugador"
        assert race_state.finish_order[0][2] is True

    def test_results_format_time_correctly(self, race_state):
        from src.states.gameover_state import GameOverState
        gos = GameOverState(MagicMock())
        assert gos._format_time(0) == "00:00.00"
        assert gos._format_time(61.5) == "01:01.50"
        assert gos._format_time(3661) == "61:01.00"
