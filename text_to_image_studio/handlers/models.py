from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/v1/models", tags=["models"])


@router.get("")
def list_models(request: Request) -> list[dict]:
    ctx = request.app.state.ctx
    out: list[dict] = []
    for mid in ctx.registry.list_ids():
        entry = ctx.registry.get(mid)
        out.append({"id": entry.id, "kind": entry.kind, "sha256": entry.sha256, "meta": entry.meta})
    return out


@router.post("/rescan")
def rescan(request: Request) -> dict:
    ctx = request.app.state.ctx
    return {"discovered": ctx.registry.scan()}


@router.get("/{model_id:path}")
def get_model(model_id: str, request: Request) -> dict:
    ctx = request.app.state.ctx
    try:
        entry = ctx.registry.get(model_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": entry.id, "kind": entry.kind, "path": str(entry.path), "meta": entry.meta}