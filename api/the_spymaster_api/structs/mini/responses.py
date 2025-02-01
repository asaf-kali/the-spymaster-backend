from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from codenames.mini.state import MiniGameState
from the_spymaster_api.structs.abstract.responses import (
    ClueResponse,
    GetGameStateResponse,
    GuessResponse,
    NextMoveResponse,
    StartGameResponse,
)


class MiniStartGameResponse(StartGameResponse[MiniGameState]):
    pass


class MiniGetGameStateResponse(GetGameStateResponse[MiniGameState]):
    pass


class MiniClueResponse(ClueResponse[MiniGameState, DuetGivenClue]):
    pass


class MiniGuessResponse(GuessResponse[MiniGameState, DuetGivenGuess]):
    pass


class MiniNextMoveResponse(NextMoveResponse[MiniGameState, DuetGivenClue, DuetGivenGuess]):
    pass
