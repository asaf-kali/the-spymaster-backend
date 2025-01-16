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
from the_spymaster_api.structs.duet.requests import StartDuetGameRequest
from the_spymaster_api.structs.duet.responses import (
    DuetClueResponse,
    DuetGetGameStateResponse,
    DuetGuessResponse,
    DuetNextMoveResponse,
    DuetStartGameResponse,
)
from the_spymaster_util.http.errors import BadRequestError
from the_spymaster_util.logger import get_logger

from server.logic.db import get_or_create, save_game
from server.models.game import DuetGame
from server.views.endpoint import HttpMethod, endpoint
from server.views.game.base import ulid_lower

log = get_logger(__name__)


class DuetGameView(GenericViewSet):

    @endpoint
    def start(self, request: StartDuetGameRequest) -> DuetStartGameResponse:
        """
        Start a new Duet game with the specified parameters.
        
        Initializes a new Duet game by creating a game board from a vocabulary in the specified language,
        setting up the initial game state, and configuring timer tokens and allowed mistakes.
        
        Parameters:
            request (StartDuetGameRequest): Request containing game initialization parameters
                - language (str): Language for the game's vocabulary
                - timer_tokens (int): Number of timer tokens for the game
                - allowed_mistakes (int): Maximum number of allowed mistakes
        
        Returns:
            DuetStartGameResponse: Response containing the newly created game's details
                - game_id (str): Unique identifier for the created game
                - game_state (DuetGameState): Initial state of the Duet game
        
        Side Effects:
            - Creates a new DuetGame in the database
            - Logs the game start with the generated game ID
        """
        vocabulary = get_vocabulary(language=request.language)
        board = DuetBoard.from_vocabulary(vocabulary=vocabulary)
        game_state = DuetGameState.from_board(board=board)
        game_state.timer_tokens = request.timer_tokens
        game_state.allowed_mistakes = request.allowed_mistakes
        game = DuetGame(id=ulid_lower(), state_data=game_state.model_dump())
        save_game(game)
        log.info(f"Starting game: {game.id}")
        return DuetStartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def clue(self, request: ClueRequest) -> DuetClueResponse:
        """
        Provide a clue for a Duet game, processing the clue and updating the game state.
        
        Retrieves an existing Duet game or creates a new one based on the provided game ID. 
        Processes the clue with optional word targeting and updates the game state accordingly.
        
        Parameters:
            request (ClueRequest): The clue request containing:
                - game_id (str): Unique identifier for the game
                - word (str): The clue word to be given
                - card_amount (int): Number of cards the clue is intended to cover
                - for_words (Optional[List[str]]): Specific words the clue is targeting
        
        Returns:
            DuetClueResponse: Contains:
                - given_clue (Clue): The processed clue
                - game_state (DuetGameState): Updated game state after processing the clue
        
        Raises:
            Potential exceptions from get_or_create, process_clue, or save_game operations
        """
        game = get_or_create(request.game_id, game_type=DuetGame)
        game_state = game.state
        for_words = tuple(request.for_words) if request.for_words else None
        clue = Clue(word=request.word, card_amount=request.card_amount, for_words=for_words)
        given_clue = game_state.process_clue(clue)
        game.state_data = game_state.model_dump()
        save_game(game)
        return DuetClueResponse(given_clue=given_clue, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> DuetGuessResponse:
        """
        Process a guess in a Duet game and update the game state.
        
        Handles a player's guess by retrieving the game instance, processing the guess through the game state,
        and updating the game's persistent state.
        
        Parameters:
            request (GuessRequest): The guess request containing the game ID and card index to guess.
        
        Returns:
            DuetGuessResponse: A response containing the processed guess and the updated game state.
        
        Side Effects:
            - Modifies the game's state in the database
            - Saves the updated game state after processing the guess
        """
        game = get_or_create(request.game_id, game_type=DuetGame)
        game_state = game.state
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.model_dump()
        save_game(game)
        return DuetGuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> DuetGetGameStateResponse:
        """
        Retrieve the current state of a Duet game.
        
        Fetches the game state for a specific Duet game using the provided game ID. If the game does not exist, it will be created.
        
        Parameters:
            request (GetGameStateRequest): Request containing the game ID to retrieve the state for.
        
        Returns:
            DuetGetGameStateResponse: A response object containing the current game state.
        """
        game = get_or_create(request.game_id, game_type=DuetGame)
        return DuetGetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> DuetNextMoveResponse:
        """
        Handles the next move in a Duet game, currently raising a not implemented error.
        
        This method is a placeholder for future implementation of an automated next move mechanism in the Duet game. The commented-out code suggests a planned workflow involving retrieving or creating a game, processing the next move through a handler, updating the game state, and returning a response.
        
        Parameters:
            request (NextMoveRequest): Request containing game ID, solver, and model identifier for determining the next move.
        
        Returns:
            DuetNextMoveResponse: Response representing the result of the next move (currently not implemented).
        
        Raises:
            BadRequestError: Indicates that the next move functionality is not yet implemented.
        """
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
