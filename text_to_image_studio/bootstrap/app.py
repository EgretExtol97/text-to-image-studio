"""FastAPI app factory. Wires ingest handlers, processors, and output drivers."""
from __future__ import annotations

from fastapi import FastAPI

from text_to_image_studio.bootstrap.runtime import RuntimeContext
from text_to_image_studio.handlers.generate import router as generate_router
from text_to_image_studio.handlers.gallery import router as gallery_router
from text_to_image_studio.handlers.health import router as health_router
from text_to_image_studio.handlers.models import router as models_router


def build_app(ctx: RuntimeContext) -> FastAPI:
    app = FastAPI(
        title="text-to-image-studio",
        version="0.9.4",
        description="Desktop text-to-image generation pipeline.",
    )
    app.state.ctx = ctx
    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(generate_router)
    app.include_router(gallery_router)
    return app