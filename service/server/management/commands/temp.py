# pylint: skip-file

import json
import logging

from django.core.management import BaseCommand

from server.models.game import ClassicGame

log = logging.getLogger(__name__)


def _fix_game_state_json():
    for game in ClassicGame.objects.all():
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
