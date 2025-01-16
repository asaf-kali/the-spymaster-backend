import logging

from the_spymaster_solvers_api.structs.requests import LoadModelsRequest
from the_spymaster_solvers_api.structs.responses import LoadModelsResponse
from the_spymaster_util.http.base_client import DEFAULT_RETRY_STRATEGY, BaseHttpClient
from urllib3 import Retry

from .structs import (
    SERVICE_ERRORS,
    ClueRequest,
    GetGameStateRequest,
    GuessRequest,
    NextMoveRequest,
)
from .structs.classic.requests import StartClassicGameRequest
from .structs.classic.responses import (
    ClassicClueResponse,
    ClassicGetGameStateResponse,
    ClassicGuessResponse,
    ClassicNextMoveResponse,
    ClassicStartGameResponse,
)

log = logging.getLogger(__name__)


class TheSpymasterClient(BaseHttpClient):
    def __init__(self, base_url: str, retry_strategy: Retry | None = DEFAULT_RETRY_STRATEGY):
        """
        Initialize a new TheSpymasterClient instance for interacting with the game API.
        
        Parameters:
            base_url (str): The base URL of the API service
            retry_strategy (Retry, optional): Strategy for handling request retries. 
                Defaults to the predefined DEFAULT_RETRY_STRATEGY if not specified.
        
        Initializes the client by:
            - Constructing the full API endpoint URL by appending '/api/v1/game' to the base URL
            - Setting up retry mechanism for handling transient errors
            - Configuring common service-level error handling
        """
        super().__init__(
            base_url=f"{base_url}/api/v1/game",
            retry_strategy=retry_strategy,
            common_errors=SERVICE_ERRORS,
        )

    def start_classic_game(self, request: StartClassicGameRequest) -> ClassicStartGameResponse:
        """
        Start a new classic game with the provided configuration.
        
        Sends a POST request to initiate a classic game using the specified game parameters.
        
        Parameters:
            request (StartClassicGameRequest): Configuration details for starting a new classic game.
        
        Returns:
            ClassicStartGameResponse: Response containing the initial game state and details after game creation.
        
        Raises:
            HTTPError: If the API request fails or returns an error status.
        """
        data: dict = self.post(endpoint="classic/start/", data=request.model_dump(), error_types={})  # type: ignore
        return ClassicStartGameResponse(**data)

    def clue(self, request: ClueRequest) -> ClassicClueResponse:
        """
        Send a clue for a classic Spymaster game.
        
        Sends a clue request to the game server and returns the server's response.
        
        Parameters:
            request (ClueRequest): The clue details to be submitted, containing information 
                                   about the word and number of associated cards.
        
        Returns:
            ClassicClueResponse: The server's response after processing the clue, 
                                 which includes game state and validation results.
        
        Raises:
            HTTPError: If there's an error communicating with the game server.
            ValidationError: If the request data is invalid.
        """
        data: dict = self.post(endpoint="classic/clue/", data=request.model_dump())  # type: ignore
        return ClassicClueResponse(**data)

    def guess(self, request: GuessRequest) -> ClassicGuessResponse:
        """
        Submit a guess in the classic Spymaster game.
        
        Sends a POST request to the game's guess endpoint with the provided guess details.
        
        Parameters:
            request (GuessRequest): The details of the guess to be submitted, including 
                                    relevant game and word information.
        
        Returns:
            ClassicGuessResponse: The response from the server after processing the guess, 
                                  containing game state and result information.
        
        Raises:
            HTTPError: If there's an error communicating with the game server.
            ValidationError: If the request data is invalid.
        """
        data: dict = self.post(endpoint="classic/guess/", data=request.model_dump())  # type: ignore
        return ClassicGuessResponse(**data)

    def next_move(self, request: NextMoveRequest) -> ClassicNextMoveResponse:
        """
        Send a request to determine the next move in a classic Spymaster game.
        
        Parameters:
            request (NextMoveRequest): A request object containing parameters for determining the next game move.
        
        Returns:
            ClassicNextMoveResponse: A response object representing the result of the next move request, 
            including game state, recommended actions, or other relevant game progression information.
        
        Raises:
            HTTPError: If there's an error communicating with the game API.
            ValidationError: If the request data is invalid or cannot be processed.
        """
        data: dict = self.post(endpoint="classic/next-move/", data=request.model_dump())  # type: ignore
        return ClassicNextMoveResponse(**data)

    def get_game_state(self, request: GetGameStateRequest) -> ClassicGetGameStateResponse:
        """
        Retrieve the current state of a classic Spymaster game.
        
        Parameters:
            request (GetGameStateRequest): Request object containing parameters for fetching the game state.
        
        Returns:
            ClassicGetGameStateResponse: A response object representing the current state of the game.
        
        Sends a GET request to the 'classic/state/' endpoint with the request data and constructs a game state response.
        """
        data: dict = self.get(endpoint="classic/state/", data=request.model_dump())  # type: ignore
        return ClassicGetGameStateResponse(**data)

    def load_models(self, request: LoadModelsRequest) -> LoadModelsResponse:
        """
        Load machine learning models for the game via the API.
        
        Parameters:
            request (LoadModelsRequest): Request object containing model loading parameters
        
        Returns:
            LoadModelsResponse: Response object with details about the loaded models
        
        Raises:
            HTTPError: If the API request fails
            ValueError: If the request data is invalid
        """
        data: dict = self.post(endpoint="load-models/", data=request.model_dump())  # type: ignore
        return LoadModelsResponse(**data)

    def raise_error(self, request: dict):
        return self.get(endpoint="raise-error/", data=request)
