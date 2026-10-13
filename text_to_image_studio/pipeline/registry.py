"""Model registry. Scans disk, hashes weights, exposes lookup by id."""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from text_to_image_studio.pipeline.errors import ModelNotFound

log = logging.getLogger("ttis.registry")

_WEIGHT_SUFFIXES = {".safetensors", ".ckpt", ".bin"}
_KIND_DIRS = {"checkpoints": "checkpoint", "loras": "lora", "vae": "vae", "controlnet": "controlnet"}


@dataclass(slots=True)
class ModelEntry:
    id: str
    kind: str
    path: Path
    sha256: str
    meta: dict = field(default_factory=dict)


class ModelRegistry:
    def __init__(self, models_dir: Path) -> None:
        self.models_dir = Path(models_dir)
        self._entries: dict[str, ModelEntry] = {}

    def scan(self) -> int:
        self._entries.clear()
        for sub, kind in _KIND_DIRS.items():
            root = self.models_dir / sub
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.suffix.lower() not in _WEIGHT_SUFFIXES:
                    continue
                mid = f"{kind}:{path.stem}"
                self._entries[mid] = ModelEntry(
                    id=mid,
                    kind=kind,
                    path=path,
                    sha256=self._hash(path),
                    meta=self._sidecar_meta(path),
                )
        log.info("registry scanned %d assets", len(self._entries))
        return len(self._entries)

    def get(self, model_id: str) -> ModelEntry:
        entry = self._entries.get(model_id)
        if entry is None:
            raise ModelNotFound(model_id)
        return entry

    def list_ids(self) -> list[str]:
        return sorted(self._entries)

    @staticmethod
    def _hash(path: Path, chunk: int = 1 << 20) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            while block := fh.read(chunk):
                h.update(block)
        return h.hexdigest()

    @staticmethod
    def _sidecar_meta(path: Path) -> dict:
        sidecar = path.with_suffix(path.suffix + ".json")
        if sidecar.exists():
            try:
                return json.loads(sidecar.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                log.warning("bad sidecar json: %s", sidecar)
        return {}