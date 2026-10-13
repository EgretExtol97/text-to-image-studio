"""Scheduler factory. Maps friendly names to diffusers schedulers."""
from __future__ import annotations

from diffusers import (
    DDIMScheduler,
    DPMSolverMultistepScheduler,
    EulerAncestralDiscreteScheduler,
    EulerDiscreteScheduler,
    UniPCMultistepScheduler,
)

_SAMPLERS = {
    "euler": lambda: EulerDiscreteScheduler(),
    "euler_a": lambda: EulerAncestralDiscreteScheduler(),
    "dpmpp_2m": lambda: DPMSolverMultistepScheduler(algorithm_type="dpmsolver++"),
    "dpmpp_2m_karras": lambda: DPMSolverMultistepScheduler(
        algorithm_type="dpmsolver++", use_karras_sigmas=True
    ),
    "unipc": lambda: UniPCMultistepScheduler(),
    "ddim": lambda: DDIMScheduler(),
}


def build_scheduler(name: str):
    factory = _SAMPLERS.get(name)
    if factory is None:
        raise KeyError(f"unknown sampler: {name!r}; known: {sorted(_SAMPLERS)}")
    return factory()