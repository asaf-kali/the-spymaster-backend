from codenames.classic.state import ClassicGameState
from the_spymaster_api.structs.classic.responses import ClassicNextMoveResponse

from server.logic.next_move import NextMoveHandler


class ClassicNextMoveHandler(NextMoveHandler[ClassicGameState, ClassicNextMoveResponse]):
    pass
