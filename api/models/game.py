from enum import Enum
from typing import Dict, Optional

from codenames.game import GameState
from codenames.utils.loader.model_loader import ModelIdentifier
from django.db import models
from pydantic import BaseModel


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @property
    def pass_probability(self) -> float:
        return DIFFICULTY_TO_PASS_PROBABILITY[self]


class Solver(str, Enum):
    NAIVE = "naive"
    OLYMPIC = "olympic"
    SNA = "sna"


class GameConfig(BaseModel):
    language: str = "hebrew"
    difficulty: Difficulty = Difficulty.EASY
    solver: Solver = Solver.NAIVE
    model_identifier: Optional[ModelIdentifier] = None


DIFFICULTY_TO_PASS_PROBABILITY: Dict[Difficulty, float] = {
    Difficulty.EASY: 0.4,
    Difficulty.MEDIUM: 0.2,
    Difficulty.HARD: 0,
}


class Game(models.Model):
    id = models.BigAutoField(primary_key=True)
    state_data = models.JSONField()

    @property
    def state(self) -> GameState:
        return GameState(**self.state_data)
