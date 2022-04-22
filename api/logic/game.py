from threading import Thread
from typing import Optional
from uuid import uuid4

from codenames.game import DEFAULT_MODEL_ADAPTER, GameManager, QuitGame
from codenames.solvers import NaiveGuesser, NaiveHinter
from codenames.utils.loader.model_loader import (
    ModelIdentifier,
    load_model_async,
    set_language_data_folder,
)
from codenames.utils.model_adapters import HEBREW_SUFFIX_ADAPTER
from django.conf import settings

from api.logic.boards import HEBREW_BOARD_6
from the_spymaster.utils import get_logger, wrap

log = get_logger(__name__)

model_id = ModelIdentifier("hebrew", "skv-ft-150", True)
set_language_data_folder(settings.LANGUAGE_DATA_FOLDER)
load_model_async(model_identifier=model_id)
adapter = HEBREW_SUFFIX_ADAPTER if model_id.language == "hebrew" and model_id.is_stemmed else DEFAULT_MODEL_ADAPTER


def start_game_in_new_thread() -> str:
    """
    Starts a new game in a new thread.
    :return: The game id.
    """
    game_id = _create_game_id()
    game_thread = Thread(target=start_game, args=(game_id,))
    game_thread.start()
    return game_id


def start_game(game_id: str):
    """
    Starts a new game.
    :param game_id: The new game id.
    """
    log.update_context(game_id=game_id)
    log.info("Starting game...")
    game_manager = None
    try:
        blue_hinter = NaiveHinter("Einstein", model_identifier=model_id, model_adapter=adapter)
        red_hinter = NaiveHinter("Yoda", model_identifier=model_id, model_adapter=adapter)
        blue_guesser = NaiveGuesser(name="Newton", model_identifier=model_id, model_adapter=adapter)
        red_guesser = NaiveGuesser(name="Anakin", model_identifier=model_id, model_adapter=adapter)
        game_manager = GameManager(blue_hinter, red_hinter, blue_guesser, red_guesser)
        game_manager.run_game(language=model_id.language, board=HEBREW_BOARD_6)
    except QuitGame:
        log.info("Game quit")
    except:  # noqa
        log.exception(f"Error occurred in game {wrap(game_id)}")
    finally:
        _print_results(game_manager)


def _print_results(game_manager: Optional[GameManager]):
    if game_manager is None:
        return
    log.info(f"\n{game_manager.board}\n")
    hint_strings = [str(hint) for hint in game_manager.raw_hints]
    hints_string = "\n".join(hint_strings)
    log.info(f"Hints:\n{hints_string}\n")
    # guess_string = "\n".join([str(guess) for guess in game_manager.given_guesses])
    # log.info(f"Guesses:\n{guess_string}\n")
    log.info(f"Winner: {game_manager.winner}")


def _create_game_id() -> str:
    return uuid4().hex[:6]
