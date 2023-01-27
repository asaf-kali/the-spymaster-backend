from the_spymaster_util.http.errors import ApiError, NotFoundError
from the_spymaster_util.logger import wrap


class SpymasterError(ApiError):
    pass


class GameDoesNotExistError(NotFoundError):
    def __init__(self, game_id: str):
        super().__init__(message=f"Game {wrap(game_id)} does not exist.", details={"game_id": game_id})


SERVICE_ERRORS = frozenset({SpymasterError, GameDoesNotExistError})
