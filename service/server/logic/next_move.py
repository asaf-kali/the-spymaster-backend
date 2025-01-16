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
        """
        Initialize a NextMoveHandler for managing game moves in Codenames.
        
        Parameters:
            game_state (ClassicGameState): The current state of the Codenames game.
            solver (Solver): The solver used for generating clues or guesses.
            model_identifier (APIModelIdentifier, optional): Identifier for the specific AI model being used. Defaults to None.
        
        Attributes:
            game_state (ClassicGameState): Stores the current game state.
            solver (Solver): Stores the solver for move generation.
            model_identifier (APIModelIdentifier): Stores the optional model identifier.
            solvers_client (TheSpymasterSolversClient): Client for interacting with the solvers backend, initialized with the configured base URL.
        """
        self.game_state = game_state
        self.solver = solver
        self.model_identifier = model_identifier
        self.solvers_client = TheSpymasterSolversClient(base_url=config.solvers_backend_url)
        # self.model_adapter = get_adapter_for_model(self.model_identifier)

    def handle(self) -> ClassicNextMoveResponse:
        """
        Determine and execute the next move based on the current game state and player role.
        
        Checks if the game is over and raises a BadRequestError if it is. Depending on the current player's role 
        (Spymaster or Operative), it calls the appropriate method to generate the next move.
        
        Raises:
            BadRequestError: If the game is already over.
            ValueError: If the current player role is not recognized.
        
        Returns:
            ClassicNextMoveResponse: The next move for the current player, which includes the updated game state, 
            solver information, model identifier, and either a clue (for Spymaster) or a guess (for Operative).
        """
        if self.game_state.is_game_over:
            raise BadRequestError(message="Game is over")
        if self.game_state.current_player_role == PlayerRole.SPYMASTER:
            return self._make_spymaster_move()
        if self.game_state.current_player_role == PlayerRole.OPERATIVE:
            return self._make_operative_move()
        raise ValueError(f"Unknown player role: {self.game_state.current_player_role}")

    def _make_spymaster_move(self) -> ClassicNextMoveResponse:
        """
        Generate a clue for the current game state as a Spymaster.
        
        Generates a clue using the current game state, an optional model identifier, and a solver. 
        The clue is processed through the game state and returned along with relevant metadata.
        
        Parameters:
            None (uses instance attributes)
        
        Returns:
            ClassicNextMoveResponse: A response containing:
                - Updated game state
                - Solver used to generate the clue
                - Model identifier used
                - Processed clue for the game
        
        Raises:
            Potential exceptions from solvers_client.generate_clue() or game_state.process_clue()
        """
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
        """
        Generate a guess for the operative player in the Codenames game.
        
        Generates a guess based on the current game state using the configured solver and model. 
        Processes the suggested guess against the game state and returns a response with the updated 
        game state and guess details.
        
        Parameters:
            None (uses instance attributes)
        
        Returns:
            ClassicNextMoveResponse: A response containing:
                - Updated game state after processing the guess
                - Solver used to generate the guess
                - Model identifier used for guess generation
                - The processed guess
        
        Raises:
            Potential exceptions from solvers_client.generate_guess() or game_state.process_guess()
        """
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
