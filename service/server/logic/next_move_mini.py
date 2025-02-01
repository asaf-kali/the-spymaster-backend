from codenames.duet.state import DuetSideState
from the_spymaster_api.structs.mini.responses import MiniNextMoveResponse

from server.logic.next_move import NextMoveHandler


class MiniNextMoveHandler(NextMoveHandler[DuetSideState, MiniNextMoveResponse]):
    pass
