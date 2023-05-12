import time
from typing import Any, Dict

from pynamodb.attributes import JSONAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.exceptions import DoesNotExist as PynamoDoesNotExist
from pynamodb.models import Model
from the_spymaster_api.structs import GameDoesNotExistError

from server.models.game import Game
from the_spymaster.config import get_config

config = get_config()


def get_game_item_id(game_id: str) -> str:
    return f"game::{game_id}"


class GameItem(Model):
    class Meta:
        table_name = config.game_items_table_name
        host = config.dynamo_db_host

    item_id = UnicodeAttribute(hash_key=True)
    state_data = JSONAttribute(null=True)
    updated_ts = NumberAttribute()

    def save(self, *args, **kwargs) -> Dict[str, Any]:
        self.updated_ts = int(time.time())
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls, game_id: str, *args, **kwargs) -> "GameItem":
        hash_key = get_game_item_id(game_id=game_id)
        return super().get(*args, hash_key=hash_key, **kwargs)  # type: ignore


def load_game(game_id: str) -> Game:
    try:
        game_item = GameItem.load(game_id=game_id)
    except PynamoDoesNotExist as e:  # pylint: disable=invalid-name
        raise GameDoesNotExistError.create(game_id=game_id) from e
    return Game(id=game_id, state_data=game_item.state_data)


def save_game(game: Game) -> None:
    item_id = get_game_item_id(game_id=game.id)
    game_item = GameItem(item_id=item_id, state_data=game.state_data)
    game_item.save()
