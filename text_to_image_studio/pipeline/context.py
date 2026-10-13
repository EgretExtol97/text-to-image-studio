"""PipelineContext: per-request state handed to processors and drivers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PipelineContext:
    job_id: str
    prompt: str
    negative_prompt: str
    seed: int
    width: int
    height: int
    steps: int
    cfg: float
    sampler: str
    model_id: str
    loras: list[str] = field(default_factory=list)
    controlnet: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    output_paths: list[Path] = field(default_factory=list)
    timings_ms: dict[str, float] = field(default_factory=dict)