# pylint: disable=R0801
from codenames.duet.board import DuetBoard
from codenames.generic.move import Clue, Guess
from codenames.mini.state import MiniGameState
from codenames.utils.vocabulary.languages import get_vocabulary
from rest_framework.viewsets import GenericViewSet
from the_spymaster_api.structs import (
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from the_spymaster_api.structs.mini.requests import MiniStartGameRequest
from the_spymaster_api.structs.mini.responses import (
    MiniClueResponse,
    MiniGetGameStateResponse,
    MiniGuessResponse,
    MiniNextMoveResponse,
    MiniStartGameResponse,
)
from the_spymaster_util.logger import get_logger

from server.logic.db import load_game, save_game
from server.logic.next_move_mini import MiniNextMoveHandler
from server.models.game import MiniGame
from server.views.endpoint import HttpMethod, endpoint
from server.views.game.base import ulid_lower

log = get_logger(__name__)


class MiniGameView(GenericViewSet):

    @endpoint
    def start(self, request: MiniStartGameRequest) -> MiniStartGameResponse:
        vocabulary = get_vocabulary(language=request.language)
        board = DuetBoard.from_vocabulary(vocabulary=vocabulary, green_amount=request.total_points)
        game_state = MiniGameState.from_board(board=board)
        game_state.timer_tokens = request.timer_tokens
        game_state.allowed_mistakes = request.allowed_mistakes
        game = MiniGame(id=ulid_lower(), state_data=game_state.model_dump())
        save_game(game)
        log.info(f"Starting mini game: {game.id}")
        return MiniStartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def clue(self, request: ClueRequest) -> MiniClueResponse:
        game = load_game(request.game_id, game_type=MiniGame)
        game_state = game.state
        log.debug(f"Processing clue for game [{game.id}]: [{request.word}]")
        for_words = tuple(request.for_words) if request.for_words else None
        clue = Clue(word=request.word, card_amount=request.card_amount, for_words=for_words)
        given_clue = game_state.process_clue(clue)
        game.state_data = game_state.model_dump()
        save_game(game)
        return MiniClueResponse(given_clue=given_clue, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> MiniGuessResponse:
        game = load_game(request.game_id, game_type=MiniGame)
        game_state = game.state
        log.debug(f"Processing guess for game [{game.id}]: [{request.card_index}]")
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.model_dump()
        save_game(game)
        return MiniGuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> MiniGetGameStateResponse:
        game = load_game(request.game_id, game_type=MiniGame)
        return MiniGetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> MiniNextMoveResponse:
        game = load_game(request.game_id, game_type=MiniGame)
        game_state = game.state
        handler = MiniNextMoveHandler(
            game_id=game.id,
            game_state=game_state,
            solver=request.solver,
            model_identifier=request.model_identifier,
        )
        response = handler.handle()
        game.state_data = handler.game_state.model_dump()
        save_game(game)
        return response
