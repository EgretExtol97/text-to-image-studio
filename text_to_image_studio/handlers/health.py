from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz(request: Request) -> dict:
    ctx = request.app.state.ctx
    return {
        "status": "ok",
        "version": "0.9.4",
        "models": len(ctx.registry.list_ids()),
        "workers": ctx.settings.max_workers,
        "device": ctx.settings.device,
    }