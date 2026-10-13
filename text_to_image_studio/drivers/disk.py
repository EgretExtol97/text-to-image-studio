"""Disk output driver. Writes PNG with embedded prompt metadata."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo


class DiskOutputDriver:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, image: Image, *, job_id: str, seed: int, index: int = 0) -> Path:
        day = dt.datetime.utcnow().strftime("%Y-%m-%d")
        folder = self.root / day
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{job_id[:8]}_{seed}_{index:02d}.png"
        path = folder / name

        meta = PngInfo()
        meta.add_text("job_id", job_id)
        meta.add_text("seed", str(seed))
        meta.add_text("generator", "text-to-image-studio/0.9.4")
        image.save(path, format="PNG", pnginfo=meta, optimize=True)
        return path

    def exists(self, path: Path) -> bool:
        return Path(path).exists()