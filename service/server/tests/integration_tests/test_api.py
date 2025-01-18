import json
from unittest.mock import ANY

from rest_framework.test import APIClient
from the_spymaster_api.structs.classic.responses import ClassicStartGameResponse

from server.tests.spymaster_test import SpymasterTest
from server.tests.util.deep_diff import deep_diff

START_GAME_PATH = "game/classic/start/"
CLUE_PATH = "game/classic/clue/"


class TestApi(SpymasterTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.api_client = APIClient()

    def test_start_game(self):
        response = self._post(START_GAME_PATH, data={})
        assert response.status_code == 200
        expected_data = {
            "game_id": ANY,
            "game_state": {
                "board": {"language": "english", "cards": ANY},
                "score": {
                    "blue": {"total": lambda x: x >= 8, "revealed": 0},
                    "red": {"total": lambda x: x >= 8, "revealed": 0},
                },
                "current_team": lambda x: x in {"BLUE", "RED"},
                "current_player_role": "SPYMASTER",
                "left_guesses": 0,
                "winner": None,
                "given_clues": [],
                "clues": [],
                "given_guesses": [],
            },
        }
        actual_data = response.json()
        diff = deep_diff(expected_data, actual_data)
        assert diff is None

    def test_clue(self):
        start_game_response = self._start_game()
        data = {
            "game_id": start_game_response.game_id,
            "word": "test",
            "card_amount": 2,
            "for_words": ["word1", "word2"],
        }
        response = self._post(path=CLUE_PATH, data=data)
        assert response.status_code == 200
        expected_data = {
            "given_clue": {"word": "test", "card_amount": 2, "team": "BLUE"},
            "game_state": {
                "board": ANY,
                "score": {"blue": {"total": 9, "revealed": 0}, "red": {"total": 8, "revealed": 0}},
                "current_team": "BLUE",
                "current_player_role": "OPERATIVE",
                "given_clues": [{"word": "test", "card_amount": 2, "team": "BLUE"}],
                "given_guesses": [],
                "left_guesses": 3,
                "winner": None,
                "clues": [{"word": "test", "card_amount": 2, "for_words": ["word1", "word2"]}],
            },
        }
        actual_data = response.json()
        diff = deep_diff(expected_data, actual_data)
        assert diff is None

    def _url(self, path):
        return f"/api/v1/{path}"

    def _post(self, path: str, data: dict):
        url = self._url(path)
        _data = json.dumps(data)
        return self.api_client.post(path=url, data=_data, content_type="application/json")

    def _start_game(self) -> ClassicStartGameResponse:
        response = self._post(path=START_GAME_PATH, data={"first_team": "BLUE"})
        return ClassicStartGameResponse.model_validate(response.json())

    # def test_guess(self):
    #     request_data = {"game_id": 1, "card_index": 0}
    #     response = self.api_client.post(f"{API_V1}/game/guess/", data=request_data)
    #     assert response.status_code == 200
    #     expected_data = {
    #         "given_guess": {"card_index": 0, "card_color": "NEUTRAL"},
    #         "game_state": ANY,
    #     }
    #     actual_data = response.json()
    #     diff = deep_diff(expected_data, actual_data)
    #     assert diff is None
    #
    # def test_next_move(self):
    #     request_data = {"game_id": 1, "solver": "dummy", "model_identifier": "dummy"}
    #     with patch("server.logic.next_move.NextMoveHandler.handle") as mock_handle:
    #         mock_handle.return_value = {"test": "data"}
    #         response = self.api_client.post(f"{API_V1}/game/next-move/", data=request_data)
    #         assert response.status_code == 200
    #         expected_data = {"test": "data"}
    #         actual_data = response.json()
    #         assert expected_data == actual_data
    #         mock_handle.assert_called_once()
