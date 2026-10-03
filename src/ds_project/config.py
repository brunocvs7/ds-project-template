"""Parâmetros do experimento."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    target: str = "target"
    seed: int = int(os.getenv("SEED", "42"))
    test_size: float = 0.2


CONFIG = Config()
