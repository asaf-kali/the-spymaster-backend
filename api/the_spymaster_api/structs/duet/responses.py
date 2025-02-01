from codenames.duet.state import DuetGameState
from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from the_spymaster_api.structs.abstract.responses import (
    ClueResponse,
    GetGameStateResponse,
    GuessResponse,
    NextMoveResponse,
    StartGameResponse,
)


class DuetStartGameResponse(StartGameResponse[DuetGameState]):
    pass


class DuetGetGameStateResponse(GetGameStateResponse[DuetGameState]):
    pass


class DuetClueResponse(ClueResponse[DuetGameState, DuetGivenClue]):
    pass


class DuetGuessResponse(GuessResponse[DuetGameState, DuetGivenGuess]):
    pass


class DuetNextMoveResponse(NextMoveResponse[DuetGameState, DuetGivenClue, DuetGivenGuess]):
    pass
