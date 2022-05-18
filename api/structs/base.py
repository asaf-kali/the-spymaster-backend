from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel
from solvers.models import ModelIdentifier

JsonType = Union[str, int, float, bool, list, Dict[str, Any], None]


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
    language: str = "english"
    difficulty: Difficulty = Difficulty.EASY
    solver: Solver = Solver.NAIVE
    model_identifier: Optional[ModelIdentifier] = None


DIFFICULTY_TO_PASS_PROBABILITY: Dict[Difficulty, float] = {
    Difficulty.EASY: 0.4,
    Difficulty.MEDIUM: 0.2,
    Difficulty.HARD: 0,
}
