from typing import Optional

from codenames.game import GameState, PlayerRole
from solvers.models import ModelIdentifier
from solvers.naive import NaiveGuesser, NaiveHinter
from the_spymaster_util import get_logger

from api.logic.errors import BadRequestError
from api.logic.language import DEFAULT_MODELS, get_adapter_for_model
from api.models.game import Game
from api.structs import Solver
from api.structs.response import NextMoveResponse

log = get_logger(__name__)


class NextMoveHandler:
    def __init__(self, game_state: GameState, solver: Solver, model_identifier: Optional[ModelIdentifier] = None):
        self.game_state = game_state
        self.solver = solver
        self.model_identifier = model_identifier or DEFAULT_MODELS[game_state.language]
        self.model_adapter = get_adapter_for_model(self.model_identifier)

    def handle(self) -> NextMoveResponse:
        if self.game_state.is_game_over:
            raise BadRequestError("Game is over")
        if self.game_state.current_player_role == PlayerRole.HINTER:
            return self._make_hinter_move()
        elif self.game_state.current_player_role == PlayerRole.GUESSER:
            return self._make_guesser_move()
        raise ValueError(f"Unknown player role: {self.game_state.current_player_role}")

    def _make_hinter_move(self) -> NextMoveResponse:
        if self.solver == Solver.NAIVE:
            hinter = NaiveHinter(name="Auto", model_identifier=self.model_identifier, model_adapter=self.model_adapter)
        else:
            raise NotImplementedError(f"Solver {self.solver} not implemented")
        hinter.team_color = self.game_state.current_team_color
        hinter.on_game_start(language=self.game_state.language, board=self.game_state.board)
        hint = hinter.pick_hint(self.game_state.hinter_state)
        given_hint = self.game_state.process_hint(hint)
        return NextMoveResponse(
            game_state=self.game_state,
            used_solver=self.solver,
            used_model_identifier=self.model_identifier,
            given_hint=given_hint,
        )

    def _make_guesser_move(self) -> NextMoveResponse:
        if self.solver == Solver.NAIVE:
            guesser = NaiveGuesser(
                name="Auto", model_identifier=self.model_identifier, model_adapter=self.model_adapter
            )
        else:
            raise NotImplementedError(f"Solver {self.solver} not implemented")
        guesser.team_color = self.game_state.current_team_color
        guesser.on_game_start(language=self.game_state.language, board=self.game_state.board)
        guess = guesser.guess(self.game_state.guesser_state)
        given_guess = self.game_state.process_guess(guess)
        return NextMoveResponse(
            game_state=self.game_state,
            used_solver=self.solver,
            used_model_identifier=self.model_identifier,
            given_guess=given_guess,
        )


def get_game(game_id: int) -> Game:
    try:
        return Game.objects.get(id=game_id)
    except Game.DoesNotExist as e:
        raise BadRequestError("Game does not exist") from e
