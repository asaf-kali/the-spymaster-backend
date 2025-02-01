from codenames.classic.board import ClassicBoard
from codenames.classic.state import ClassicGameState
from codenames.generic.move import Clue, Guess
from codenames.utils.vocabulary.languages import get_vocabulary
from rest_framework.viewsets import GenericViewSet
from the_spymaster_api.structs import (
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from the_spymaster_api.structs.classic.requests import ClassicStartGameRequest
from the_spymaster_api.structs.classic.responses import (
    ClassicClueResponse,
    ClassicGetGameStateResponse,
    ClassicGuessResponse,
    ClassicNextMoveResponse,
    ClassicStartGameResponse,
)
from the_spymaster_util.logger import get_logger

from server.logic.db import load_game, save_game
from server.logic.next_move_classic import ClassicNextMoveHandler
from server.models.game import ClassicGame
from server.views.endpoint import HttpMethod, endpoint
from server.views.game.base import ulid_lower

log = get_logger(__name__)


class ClassicGameView(GenericViewSet):

    @endpoint
    def start(self, request: ClassicStartGameRequest) -> ClassicStartGameResponse:
        vocabulary = get_vocabulary(language=request.language)
        board = ClassicBoard.from_vocabulary(vocabulary=vocabulary, first_team=request.first_team)
        game_state = ClassicGameState.from_board(board=board)
        game = ClassicGame(id=ulid_lower(), state_data=game_state.model_dump())
        save_game(game)
        log.info(f"Starting classic game: {game.id}")
        return ClassicStartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def clue(self, request: ClueRequest) -> ClassicClueResponse:
        game = load_game(request.game_id, game_type=ClassicGame)
        game_state = game.state
        log.debug(f"Processing clue for game [{game.id}]: [{request.word}]")
        for_words = tuple(request.for_words) if request.for_words else None
        clue = Clue(word=request.word, card_amount=request.card_amount, for_words=for_words)
        given_clue = game_state.process_clue(clue)
        game.state_data = game_state.model_dump()
        save_game(game)
        return ClassicClueResponse(given_clue=given_clue, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> ClassicGuessResponse:
        game = load_game(request.game_id, game_type=ClassicGame)
        game_state = game.state
        log.debug(f"Processing guess for game [{game.id}]: [{request.card_index}]")
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.model_dump()
        save_game(game)
        return ClassicGuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> ClassicGetGameStateResponse:
        game = load_game(request.game_id, game_type=ClassicGame)
        return ClassicGetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> ClassicNextMoveResponse:
        game = load_game(request.game_id, game_type=ClassicGame)
        game_state = game.state
        handler = ClassicNextMoveHandler(
            game_id=game.id,
            game_state=game_state,
            solver=request.solver,
            model_identifier=request.model_identifier,
        )
        response = handler.handle()
        game.state_data = handler.game_state.model_dump()
        save_game(game)
        return response
