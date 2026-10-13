"""Seed helpers. -1 means random; everything else is clamped to 32-bit."""
from __future__ import annotations

import secrets

MAX_SEED = 2**32 - 1


def normalize_seed(seed: int) -> int:
    if seed is None or seed < 0:
        return secrets.randbelow(MAX_SEED)
    return seed % (MAX_SEED + 1)