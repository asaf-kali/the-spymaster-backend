from typing import Optional

from codenames.game import (
    DEFAULT_MODEL_ADAPTER,
    GameState,
    ModelFormatAdapter,
    PlayerRole,
)
from codenames.solvers import NaiveGuesser, NaiveHinter
from codenames.utils.loader.model_loader import (
    ModelIdentifier,
    load_model_async,
    set_language_data_folder,
)
from codenames.utils.model_adapters import HEBREW_SUFFIX_ADAPTER
from django.conf import settings

from api.logic.errors import BadRequestError
from api.models.game import Game, Solver
from api.models.response import NextMoveResponse
from the_spymaster.utils import get_logger

log = get_logger(__name__)

DEFAULT_MODELS = {
    "hebrew": ModelIdentifier(language="hebrew", model_name="skv-ft-150", is_stemmed=True),
    "english": ModelIdentifier(language="english", model_name="wiki-50", is_stemmed=False),
}


# def start_game_in_new_thread() -> str:
#     """
#     Starts a new game in a new thread.
#     :return: The game id.
#     """
#     game_id = _create_game_code()
#     game_thread = Thread(target=start_game, args=(game_id,))
#     game_thread.start()
#     return game_id


# def start_game(game_id: str):
#     """
#     Starts a new game.
#     :param game_id: The new game id.
#     """
#     log.update_context(game_id=game_id)
#     log.info("Starting game...")
#     game_manager = None
#     try:
#         blue_hinter = NaiveHinter("Einstein", model_identifier=model_id, model_adapter=adapter)
#         red_hinter = NaiveHinter("Yoda", model_identifier=model_id, model_adapter=adapter)
#         blue_guesser = NaiveGuesser(name="Newton", model_identifier=model_id, model_adapter=adapter)
#         red_guesser = NaiveGuesser(name="Anakin", model_identifier=model_id, model_adapter=adapter)
#         game_state = build_game_state(language=model_id.language)
#         game_manager = GameRunner(blue_hinter, red_hinter, blue_guesser, red_guesser, state=game_state)
#         game_manager.run_game(None, None)  # noqa
#     except QuitGame:
#         log.info("Game quit")
#     except:  # noqa
#         log.exception(f"Error occurred in game {wrap(game_id)}")
#     finally:
#         _print_results(game_manager.state)


# def _print_results(game_manager: Optional[GameState]):
#     if game_manager is None:
#         return
#     log.info(f"\n{game_manager.board}\n")
#     hint_strings = [str(hint) for hint in game_manager.raw_hints]
#     hints_string = "\n".join(hint_strings)
#     log.info(f"Hints:\n{hints_string}\n")
#     # guess_string = "\n".join([str(guess) for guess in game_manager.given_guesses])
#     # log.info(f"Guesses:\n{guess_string}\n")
#     log.info(f"Winner: {game_manager.winner}")


# def _create_game_code() -> str:
#     return uuid4().hex[:6]


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


def get_adapter_for_model(model_id: ModelIdentifier) -> ModelFormatAdapter:
    return HEBREW_SUFFIX_ADAPTER if model_id.language == "hebrew" and model_id.is_stemmed else DEFAULT_MODEL_ADAPTER


def get_game(game_id: int) -> Game:
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist as e:
        raise BadRequestError("Game does not exist") from e
    return game


def _load_default_models_async(language_data_folder: Optional[str] = None):
    if language_data_folder is None:
        language_data_folder = settings.LANGUAGE_DATA_FOLDER
    log.info(f"Loading default models from {language_data_folder}")
    set_language_data_folder(language_data_folder)
    for model_id in DEFAULT_MODELS.values():
        load_model_async(model_identifier=model_id)


_load_default_models_async()
