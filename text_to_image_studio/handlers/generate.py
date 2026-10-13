from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from text_to_image_studio.pipeline.context import PipelineContext
from text_to_image_studio.utils.seeds import normalize_seed

router = APIRouter(prefix="/v1/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2048)
    negative_prompt: str = Field(default="", max_length=2048)
    model_id: str
    seed: int = -1
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=1024, ge=256, le=2048)
    steps: int = Field(default=28, ge=1, le=150)
    cfg: float = Field(default=6.5, ge=0.0, le=30.0)
    sampler: str = "dpmpp_2m_karras"
    loras: list[str] = Field(default_factory=list)
    controlnet: str | None = None


@router.post("")
def enqueue(payload: GenerateRequest, request: Request) -> dict:
    ctx_app = request.app.state.ctx
    try:
        ctx_app.registry.get(payload.model_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    job_id = str(uuid.uuid4())
    pctx = PipelineContext(
        job_id=job_id,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        seed=normalize_seed(payload.seed),
        width=payload.width,
        height=payload.height,
        steps=payload.steps,
        cfg=payload.cfg,
        sampler=payload.sampler,
        model_id=payload.model_id,
        loras=list(payload.loras),
        controlnet=payload.controlnet,
    )
    ctx_app.queue.submit(pctx)
    return {"job_id": job_id, "status": "queued", "seed": pctx.seed}