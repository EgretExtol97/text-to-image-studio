"""Layered settings: env -> local.toml -> defaults. Windows-friendly paths."""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_HOME = Path(os.environ.get("TTIS_HOME", Path.home() / ".text-to-image-studio"))


@dataclass(frozen=True, slots=True)
class Settings:
    home: Path
    models_dir: Path
    outputs_dir: Path
    db_url: str
    max_workers: int
    default_sampler: str
    default_steps: int
    default_cfg: float
    default_resolution: int
    device: str
    allow_tf32: bool
    hf_token: str | None


def _read_local_toml(home: Path) -> dict:
    cfg = home / "config" / "local.toml"
    if cfg.exists():
        with cfg.open("rb") as fh:
            return tomllib.load(fh)
    return {}


def load_settings() -> Settings:
    home = DEFAULT_HOME
    home.mkdir(parents=True, exist_ok=True)
    local = _read_local_toml(home)

    models_dir = Path(local.get("paths", {}).get("models", home / "models"))
    outputs_dir = Path(local.get("paths", {}).get("outputs", home / "outputs"))

    return Settings(
        home=home,
        models_dir=models_dir,
        outputs_dir=outputs_dir,
        db_url=local.get("db", {}).get("url", f"sqlite:///{home / 'studio.sqlite'}"),
        max_workers=int(local.get("pipeline", {}).get("max_workers", 2)),
        default_sampler=local.get("sampler", {}).get("name", "dpmpp_2m_karras"),
        default_steps=int(local.get("sampler", {}).get("steps", 28)),
        default_cfg=float(local.get("sampler", {}).get("cfg", 6.5)),
        default_resolution=int(local.get("render", {}).get("resolution", 1024)),
        device=os.environ.get("TTIS_DEVICE", "cuda"),
        allow_tf32=os.environ.get("TTIS_TF32", "1") == "1",
        hf_token=os.environ.get("HF_TOKEN"),
    )