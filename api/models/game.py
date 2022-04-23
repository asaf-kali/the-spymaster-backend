from codenames.game import GameState
from django.db import models


class Game(models.Model):
    id = models.BigAutoField(primary_key=True)
    state_json = models.JSONField()

    @property
    def state(self) -> GameState:
        return GameState.from_json(self.state_json)
