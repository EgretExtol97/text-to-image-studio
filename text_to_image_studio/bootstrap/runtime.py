"""Runtime context: model registry, job queue, output driver, db session factory."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from text_to_image_studio.config.settings import Settings, load_settings
from text_to_image_studio.drivers.disk import DiskOutputDriver
from text_to_image_studio.drivers.base import OutputDriver
from text_to_image_studio.models.db import build_engine, build_session_factory
from text_to_image_studio.pipeline.queue import JobQueue
from text_to_image_studio.pipeline.registry import ModelRegistry

log = logging.getLogger("ttis.runtime")


@dataclass
class RuntimeContext:
    settings: Settings
    registry: ModelRegistry
    queue: JobQueue
    output_driver: OutputDriver
    session_factory: sessionmaker = field(repr=False)


def init_runtime(settings: Settings | None = None) -> RuntimeContext:
    settings = settings or load_settings()
    Path(settings.outputs_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.models_dir).mkdir(parents=True, exist_ok=True)

    engine = build_engine(settings.db_url)
    session_factory = build_session_factory(engine)

    registry = ModelRegistry(settings.models_dir)
    registry.scan()

    queue = JobQueue(max_workers=settings.max_workers)
    driver: OutputDriver = DiskOutputDriver(root=Path(settings.outputs_dir))

    log.info(
        "runtime ready: models=%d workers=%d outputs=%s",
        len(registry.list_ids()),
        settings.max_workers,
        settings.outputs_dir,
    )
    return RuntimeContext(
        settings=settings,
        registry=registry,
        queue=queue,
        output_driver=driver,
        session_factory=session_factory,
    )