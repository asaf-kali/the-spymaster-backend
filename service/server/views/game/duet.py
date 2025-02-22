# pylint: disable=R0801

from codenames.duet.board import DuetBoard
from codenames.duet.state import DuetGameState
from codenames.generic.move import Clue, Guess
from codenames.utils.vocabulary.languages import get_vocabulary
from rest_framework.viewsets import GenericViewSet
from the_spymaster_api.structs import (
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from the_spymaster_api.structs.duet.requests import DuetStartGameRequest
from the_spymaster_api.structs.duet.responses import (
    DuetClueResponse,
    DuetGetGameStateResponse,
    DuetGuessResponse,
    DuetNextMoveResponse,
    DuetStartGameResponse,
)
from the_spymaster_util.http.errors import BadRequestError
from the_spymaster_util.logger import get_logger

from server.logic.db import load_game, save_game
from server.models.game import DuetGame
from server.views.endpoint import HttpMethod, endpoint
from server.views.game.base import ulid_lower

log = get_logger(__name__)


class DuetGameView(GenericViewSet):

    @endpoint
    def start(self, request: DuetStartGameRequest) -> DuetStartGameResponse:
        vocabulary = get_vocabulary(language=request.language)
        board = DuetBoard.from_vocabulary(vocabulary=vocabulary)
        game_state = DuetGameState.from_board(board=board)
        game_state.timer_tokens = request.timer_tokens
        game_state.allowed_mistakes = request.allowed_mistakes
        game = DuetGame(id=ulid_lower(), state_data=game_state.model_dump())
        save_game(game)
        log.info(f"Starting duet game: {game.id}")
        return DuetStartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def clue(self, request: ClueRequest) -> DuetClueResponse:
        game = load_game(request.game_id, game_type=DuetGame)
        game_state = game.state
        log.debug(f"Processing clue for game [{game.id}]: [{request.word}]")
        for_words = tuple(request.for_words) if request.for_words else None
        clue = Clue(word=request.word, card_amount=request.card_amount, for_words=for_words)
        given_clue = game_state.process_clue(clue)
        game.state_data = game_state.model_dump()
        save_game(game)
        return DuetClueResponse(given_clue=given_clue, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> DuetGuessResponse:
        game = load_game(request.game_id, game_type=DuetGame)
        game_state = game.state
        log.debug(f"Processing guess for game [{game.id}]: [{request.card_index}]")
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.model_dump()
        save_game(game)
        return DuetGuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> DuetGetGameStateResponse:
        game = load_game(request.game_id, game_type=DuetGame)
        return DuetGetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> DuetNextMoveResponse:
        raise BadRequestError(message="Not implemented")
        # game = get_or_create(request.game_id, game_type=DuetGame)
        # game_state = game.state
        # handler = NextMoveHandler(
        #     game_state=game_state, solver=request.solver, model_identifier=request.model_identifier
        # )
        # response = handler.handle()
        # game.state_data = handler.game_state.model_dump()
        # save_game(game)
        # return response
