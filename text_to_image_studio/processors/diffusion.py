"""Core sampling loop. Loads pipeline lazily, runs one job, hands off to driver."""
from __future__ import annotations

import logging
import time
from functools import lru_cache

from text_to_image_studio.pipeline.context import PipelineContext
from text_to_image_studio.pipeline.errors import OOMError
from text_to_image_studio.processors.prompt import compile_prompt
from text_to_image_studio.processors.sampler import build_scheduler

log = logging.getLogger("ttis.diffusion")


@lru_cache(maxsize=2)
def _load_pipe(model_path: str, device: str):
    # Imported here so the API process doesn't pull torch at import time.
    import torch
    from diffusers import StableDiffusionXLPipeline

    pipe = StableDiffusionXLPipeline.from_single_file(
        model_path,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
    )
    if device == "cuda":
        pipe.to("cuda")
        torch.backends.cuda.matmul.allow_tf32 = True
    else:
        pipe.to("cpu")
    pipe.enable_vae_tiling()
    return pipe


def run_pipeline(ctx: PipelineContext) -> PipelineContext:
    t0 = time.perf_counter()
    # Registry lookup is done by the caller; we accept the resolved path via extra.
    model_path: str = ctx.extra["model_path"]
    device: str = ctx.extra.get("device", "cuda")

    pipe = _load_pipe(model_path, device)
    positive, negative = compile_prompt(ctx.prompt, ctx.negative_prompt)
    pipe.scheduler = build_scheduler(ctx.sampler)

    t_load = time.perf_counter()
    try:
        result = pipe(
            prompt=positive,
            negative_prompt=negative,
            num_inference_steps=ctx.steps,
            guidance_scale=ctx.cfg,
            width=ctx.width,
            height=ctx.height,
            generator=_make_generator(ctx.seed, device),
        )
    except RuntimeError as exc:
        if "out of memory" in str(exc).lower():
            raise OOMError((ctx.width, ctx.height), device) from exc
        raise

    ctx.timings_ms["load"] = (t_load - t0) * 1000
    ctx.timings_ms["sample"] = (time.perf_counter() - t_load) * 1000
    ctx.extra["image"] = result.images[0]
    return ctx


def _make_generator(seed: int, device: str):
    import torch

    gen = torch.Generator(device="cuda" if device == "cuda" else "cpu")
    gen.manual_seed(seed)
    return gen