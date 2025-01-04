from __future__ import annotations

from http import HTTPStatus

from codenames.generic.exceptions import GameRuleError
from the_spymaster_util.http.errors import BadRequestError, NotFoundError


class APIGameRuleError(BadRequestError):
    @classmethod
    def from_game_rule_error(cls, error: GameRuleError) -> APIGameRuleError:
        return cls(
            message=f"Invalid move: {error}",
            http_status=HTTPStatus.BAD_REQUEST,
            data={"error": error.__class__.__name__},
        )


class GameDoesNotExistError(NotFoundError):
    @classmethod
    def create(cls, game_id: str) -> GameDoesNotExistError:
        return cls(message=f"Game {game_id} does not exist", data={"game_id": game_id})


SERVICE_ERRORS = frozenset({GameDoesNotExistError, APIGameRuleError})
