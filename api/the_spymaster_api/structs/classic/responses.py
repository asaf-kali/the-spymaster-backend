from codenames.classic.state import ClassicGameState
from codenames.classic.types import ClassicGivenClue, ClassicGivenGuess
from the_spymaster_api.structs.abstract.responses import (
    ClueResponse,
    GetGameStateResponse,
    GuessResponse,
    NextMoveResponse,
    StartGameResponse,
)


class ClassicStartGameResponse(StartGameResponse[ClassicGameState]):
    pass


class ClassicGetGameStateResponse(GetGameStateResponse[ClassicGameState]):
    pass


class ClassicClueResponse(ClueResponse[ClassicGameState, ClassicGivenClue]):
    pass


class ClassicGuessResponse(GuessResponse[ClassicGameState, ClassicGivenGuess]):
    pass


class ClassicNextMoveResponse(NextMoveResponse[ClassicGameState, ClassicGivenClue, ClassicGivenGuess]):
    pass
