import logging
from typing import Optional

from codenames.game.player import PlayerRole
from codenames.game.state import GameState
from the_spymaster_api.structs import NextMoveResponse, Solver
from the_spymaster_solvers_api.client import TheSpymasterSolversClient
from the_spymaster_solvers_api.structs.base import ModelIdentifier
from the_spymaster_solvers_api.structs.requests import (
    GenerateGuessRequest,
    GenerateHintRequest,
)
from the_spymaster_util.http.errors import BadRequestError

from the_spymaster.config import get_config

log = logging.getLogger(__name__)
config = get_config()


class NextMoveHandler:
    def __init__(self, game_state: GameState, solver: Solver, model_identifier: Optional[ModelIdentifier] = None):
        self.game_state = game_state
        self.solver = solver
        self.model_identifier = model_identifier
        self.solvers_client = TheSpymasterSolversClient(base_url=config.solvers_backend_url)
        # self.model_adapter = get_adapter_for_model(self.model_identifier)

    def handle(self) -> NextMoveResponse:
        if self.game_state.is_game_over:
            raise BadRequestError(message="Game is over")
        if self.game_state.current_player_role == PlayerRole.HINTER:
            return self._make_hinter_move()
        if self.game_state.current_player_role == PlayerRole.GUESSER:
            return self._make_guesser_move()
        raise ValueError(f"Unknown player role: {self.game_state.current_player_role}")

    def _make_hinter_move(self) -> NextMoveResponse:
        generate_hint_request = GenerateHintRequest(
            game_state=self.game_state,
            model_identifier=self.model_identifier,
            solver=self.solver,
        )
        generate_hint_response = self.solvers_client.generate_hint(request=generate_hint_request)
        given_hint = self.game_state.process_hint(hint=generate_hint_response.suggested_hint)
        return NextMoveResponse(
            game_state=self.game_state,
            used_solver=generate_hint_response.used_solver,
            used_model_identifier=generate_hint_response.used_model_identifier,
            given_hint=given_hint,
        )

    def _make_guesser_move(self) -> NextMoveResponse:
        generate_guess_request = GenerateGuessRequest(
            game_state=self.game_state,
            model_identifier=self.model_identifier,
            solver=self.solver,
        )
        generate_guess_response = self.solvers_client.generate_guess(request=generate_guess_request)
        given_guess = self.game_state.process_guess(guess=generate_guess_response.suggested_guess)
        return NextMoveResponse(
            game_state=self.game_state,
            used_solver=generate_guess_response.used_solver,
            used_model_identifier=generate_guess_response.used_model_identifier,
            given_guess=given_guess,
        )
