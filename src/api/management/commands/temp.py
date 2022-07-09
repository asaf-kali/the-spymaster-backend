import json

from django.core.management import BaseCommand
from the_spymaster_util import get_logger

from api.models.game import Game

log = get_logger(__name__)


def _fix_game_state_json():
    for game in Game.objects.all():
        state = game.state_data
        if not isinstance(state, str):
            continue
        try:
            state = json.loads(state)
        except Exception as e:
            log.error(f"Failed to load game state for game {game.id}: {e}")
            continue
        game.state_data = state
        game.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        _fix_game_state_json()