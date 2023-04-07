from unittest.mock import ANY

from rest_framework.test import APIClient

from api.tests.spymaster_test import SpymasterTest
from api.tests.util.deep_diff import deep_diff

API_V1 = "/api/v1"


class ApiTest(SpymasterTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.api_client = APIClient()

    def test_start_game(self):
        response = self.api_client.post(f"{API_V1}/game/start/")
        assert response.status_code == 200
        expected_data = {
            "game_id": ANY,
            "game_state": {
                "language": "english",
                "board": {"cards": ANY},
                "score": {
                    "blue": {"total": 9, "revealed": 0},
                    "red": {"total": 8, "revealed": 0},
                },
                "current_team_color": "BLUE",
                "current_player_role": "HINTER",
                "left_guesses": 0,
                "bonus_given": False,
                "winner": None,
                "raw_hints": [],
                "given_hints": [],
                "given_guesses": [],
            },
        }
        actual_data = response.json()
        diff = deep_diff(expected_data, actual_data)
        assert diff is None
