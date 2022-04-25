from enum import Enum

from codenames.game import GameState
from django.db import models


class Solver(str, Enum):
    NAIVE = "naive"
    OLYMPIC = "olympic"
    SNA = "sna"


class Game(models.Model):
    id = models.BigAutoField(primary_key=True)
    state_json = models.JSONField()

    @property
    def state(self) -> GameState:
        return GameState.from_json(self.state_json)
