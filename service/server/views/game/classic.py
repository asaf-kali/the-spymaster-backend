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
from the_spymaster_api.structs.classic.requests import StartClassicGameRequest
from the_spymaster_api.structs.classic.responses import (
    ClassicClueResponse,
    ClassicGetGameStateResponse,
    ClassicGuessResponse,
    ClassicNextMoveResponse,
    ClassicStartGameResponse,
)
from the_spymaster_util.logger import get_logger

from server.logic.db import get_or_create, save_game
from server.logic.next_move import NextMoveHandler
from server.models.game import ClassicGame
from server.views.endpoint import HttpMethod, endpoint
from server.views.game.base import ulid_lower

log = get_logger(__name__)


class ClassicGameView(GenericViewSet):

    @endpoint
    def start(self, request: StartClassicGameRequest) -> ClassicStartGameResponse:
        """
        Initialize a new classic Codenames game with a specified language and first team.
        
        Generates a game board using the provided language's vocabulary, creates a game state,
        and saves the game instance to the database.
        
        Parameters:
            request (StartClassicGameRequest): Request containing the game's language and first team.
        
        Returns:
            ClassicStartGameResponse: Response with the generated game ID and initial game state.
        
        Raises:
            ValueError: If vocabulary cannot be retrieved or board generation fails.
        
        Example:
            request = StartClassicGameRequest(language='english', first_team=Team.RED)
            response = classic_game_view.start(request)
            # Creates a new game with an English vocabulary and RED team starting
        """
        vocabulary = get_vocabulary(language=request.language)
        board = ClassicBoard.from_vocabulary(vocabulary=vocabulary, first_team=request.first_team)
        game_state = ClassicGameState.from_board(board=board)
        game = ClassicGame(id=ulid_lower(), state_data=game_state.model_dump())
        save_game(game)
        log.info(f"Starting game: {game.id}")
        return ClassicStartGameResponse(game_id=game.id, game_state=game_state)

    @endpoint
    def clue(self, request: ClueRequest) -> ClassicClueResponse:
        """
        Submit a clue for a classic Codenames game.
        
        Processes a clue for the specified game, updating the game state and saving the changes.
        
        Parameters:
            request (ClueRequest): The clue submission request containing:
                - game_id (str): Unique identifier for the game
                - word (str): The clue word to be given
                - card_amount (int): Number of cards associated with the clue
                - for_words (Optional[List[str]]): Optional list of specific words the clue is intended for
        
        Returns:
            ClassicClueResponse: A response containing:
                - given_clue (Clue): The processed clue
                - game_state (ClassicGameState): Updated game state after clue submission
        
        Raises:
            ValueError: If the clue cannot be processed or the game state is invalid
        """
        game = get_or_create(request.game_id, game_type=ClassicGame)
        game_state = game.state
        for_words = tuple(request.for_words) if request.for_words else None
        clue = Clue(word=request.word, card_amount=request.card_amount, for_words=for_words)
        given_clue = game_state.process_clue(clue)
        game.state_data = game_state.model_dump()
        save_game(game)
        return ClassicClueResponse(given_clue=given_clue, game_state=game_state)

    @endpoint
    def guess(self, request: GuessRequest) -> ClassicGuessResponse:
        """
        Process a guess in the classic Codenames game.
        
        Handles a player's guess by retrieving the game instance, processing the guess on the current game state, 
        and updating the game's state in the database.
        
        Parameters:
            request (GuessRequest): The guess request containing the game ID and card index to guess.
        
        Returns:
            ClassicGuessResponse: A response containing the processed guess and the updated game state.
        
        Raises:
            ValueError: If the game cannot be retrieved or the guess is invalid.
        """
        game = get_or_create(request.game_id, game_type=ClassicGame)
        game_state = game.state
        guess = Guess(card_index=request.card_index)
        given_guess = game_state.process_guess(guess)
        game.state_data = game_state.model_dump()
        save_game(game)
        return ClassicGuessResponse(given_guess=given_guess, game_state=game_state)

    @endpoint(methods=[HttpMethod.GET], url_path="state")
    def get_game_state(self, request: GetGameStateRequest) -> ClassicGetGameStateResponse:
        """
        Retrieve the current state of a classic Codenames game.
        
        Fetches the game state for a specific game using its unique identifier. If the game does not exist, it will be created.
        
        Parameters:
            request (GetGameStateRequest): Request containing the unique game identifier.
        
        Returns:
            ClassicGetGameStateResponse: Response containing the current game state.
        """
        game = get_or_create(request.game_id, game_type=ClassicGame)
        return ClassicGetGameStateResponse(game_state=game.state)

    @endpoint(url_path="next-move")
    def next_move(self, request: NextMoveRequest) -> ClassicNextMoveResponse:
        """
        Determine the next move in a classic Codenames game using a specified solver and model.
        
        Retrieves an existing game or creates a new one, initializes a NextMoveHandler with the current game state, 
        solver, and model identifier, and processes the next recommended move.
        
        Parameters:
            request (NextMoveRequest): Request containing the game ID, solver type, and optional model identifier.
        
        Returns:
            ClassicNextMoveResponse: Response containing the recommended next move and updated game state.
        
        Side Effects:
            - Updates the game state in the database
            - Modifies the game instance with the latest state data
        """
        game = get_or_create(request.game_id, game_type=ClassicGame)
        game_state = game.state
        handler = NextMoveHandler(
            game_state=game_state, solver=request.solver, model_identifier=request.model_identifier
        )
        response = handler.handle()
        game.state_data = handler.game_state.model_dump()
        save_game(game)
        return response
