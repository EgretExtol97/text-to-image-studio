from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

router = APIRouter(prefix="/v1/gallery", tags=["gallery"])


@router.get("")
def list_gallery(request: Request, limit: int = 50) -> list[dict]:
    ctx = request.app.state.ctx
    root = Path(ctx.settings.outputs_dir)
    if not root.exists():
        return []
    items: list[dict] = []
    for path in sorted(root.glob("**/*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        items.append({"name": path.name, "path": str(path.relative_to(root)), "size": path.stat().st_size})
    return items


@router.get("/file/{rel_path:path}")
def fetch_file(rel_path: str, request: Request) -> FileResponse:
    ctx = request.app.state.ctx
    root = Path(ctx.settings.outputs_dir).resolve()
    target = (root / rel_path).resolve()
    if root not in target.parents and target != root:
        raise HTTPException(status_code=400, detail="path escapes outputs dir")
    if not target.exists():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(target)