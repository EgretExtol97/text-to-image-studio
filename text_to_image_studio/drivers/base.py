"""Output driver interface. Anything that persists a finished image implements this."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL.Image import Image


class OutputDriver(Protocol):
    def write(self, image: Image, *, job_id: str, seed: int, index: int = 0) -> Path: ...
    def exists(self, path: Path) -> bool: ...