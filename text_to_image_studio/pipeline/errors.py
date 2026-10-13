"""Pipeline-specific exceptions. Keep the message actionable."""
from __future__ import annotations


class PipelineError(RuntimeError):
    """Base class for pipeline failures."""


class ModelNotFound(PipelineError):
    def __init__(self, model_id: str) -> None:
        super().__init__(f"model not found in registry: {model_id!r}")
        self.model_id = model_id


class OOMError(PipelineError):
    def __init__(self, requested: tuple[int, int], device: str) -> None:
        super().__init__(f"OOM at {requested[0]}x{requested[1]} on {device}; lower resolution or enable tiling")
        self.requested = requested
        self.device = device