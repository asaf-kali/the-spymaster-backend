import logging

from codenames.classic.state import ClassicGameState
from codenames.generic.player import PlayerRole
from the_spymaster_api.structs import Solver
from the_spymaster_api.structs.classic.responses import ClassicNextMoveResponse
from the_spymaster_solvers_api.client import TheSpymasterSolversClient
from the_spymaster_solvers_api.structs.base import APIModelIdentifier
from the_spymaster_solvers_api.structs.requests import (
    GenerateClueRequest,
    GenerateGuessRequest,
)
from the_spymaster_util.http.errors import BadRequestError

from the_spymaster.config import get_config

log = logging.getLogger(__name__)
config = get_config()


class NextMoveHandler:
    def __init__(
        self, game_state: ClassicGameState, solver: Solver, model_identifier: APIModelIdentifier | None = None
    ):
        self.game_state = game_state
        self.solver = solver
        self.model_identifier = model_identifier
        self.solvers_client = TheSpymasterSolversClient(base_url=config.solvers_backend_url)
        # self.model_adapter = get_adapter_for_model(self.model_identifier)

    def handle(self) -> ClassicNextMoveResponse:
        if self.game_state.is_game_over:
            raise BadRequestError(message="Game is over")
        if self.game_state.current_player_role == PlayerRole.SPYMASTER:
            return self._make_spymaster_move()
        if self.game_state.current_player_role == PlayerRole.OPERATIVE:
            return self._make_operative_move()
        raise ValueError(f"Unknown player role: {self.game_state.current_player_role}")

    def _make_spymaster_move(self) -> ClassicNextMoveResponse:
        generate_clue_request = GenerateClueRequest(
            spymaster_state=self.game_state,
            model_identifier=self.model_identifier,
            solver=self.solver,
        )
        generate_clue_response = self.solvers_client.generate_clue(request=generate_clue_request)
        given_clue = self.game_state.process_clue(clue=generate_clue_response.suggested_clue)
        return ClassicNextMoveResponse(
            game_state=self.game_state,
            used_solver=generate_clue_response.used_solver,
            used_model_identifier=generate_clue_response.used_model_identifier,
            given_clue=given_clue,
        )

    def _make_operative_move(self) -> ClassicNextMoveResponse:
        generate_guess_request = GenerateGuessRequest(
            operative_state=self.game_state.operative_state,
            model_identifier=self.model_identifier,
            solver=self.solver,
        )
        generate_guess_response = self.solvers_client.generate_guess(request=generate_guess_request)
        given_guess = self.game_state.process_guess(guess=generate_guess_response.suggested_guess)
        return ClassicNextMoveResponse(
            game_state=self.game_state,
            used_solver=generate_guess_response.used_solver,
            used_model_identifier=generate_guess_response.used_model_identifier,
            given_guess=given_guess,
        )
