from unittest.mock import ANY

from rest_framework.test import APIClient

from api.tests.spymaster_test import SpymasterTest

API_V1 = "/api/v1"


class ApiTest(SpymasterTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.api_client = APIClient()

    def test_start_game(self):
        response = self.api_client.post(f"{API_V1}/game/start/")
        assert response.status_code == 200
        expected_data_structure = {
            "game_id": ANY,
            "game_state": {
                "language": "english",
                "board": {"cards": ANY},
                "current_team_color": "Blue",
                "current_player_role": "Hinter",
                "left_guesses": 0,
                "bonus_given": False,
                "winner": None,
                "remaining_score": {"Blue": 9, "Red": 8},
                "raw_hints": [],
                "given_hints": [],
                "given_guesses": [],
            },
        }
        actual_data = response.json()
        assert actual_data == expected_data_structure
