"""Prompt compilation: token trimming, weight syntax, negative defaulting."""
from __future__ import annotations

import re

_WEIGHT_RE = re.compile(r"\(([^()]+):([0-9]*\.?[0-9]+)\)")
MAX_TOKENS = 75 * 3  # SDXL accepts 3 chunks of 75 before truncation


def compile_prompt(prompt: str, negative: str) -> tuple[str, str]:
    positive = _normalize(prompt)
    neg = _normalize(negative) or "lowres, blurry, watermark, text, jpeg artifacts"
    return positive, neg


def _normalize(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    text = _WEIGHT_RE.sub(lambda m: f"({m.group(1)}:{m.group(2)})", text)
    return _truncate(text)


def _truncate(text: str, max_words: int = MAX_TOKENS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])