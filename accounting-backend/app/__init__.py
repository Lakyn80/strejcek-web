"""FastAPI host for the Strejcek accounting service."""

from __future__ import annotations

from typing import Any


def create_app(*args: Any, **kwargs: Any):
    from app.main import create_app as factory

    return factory(*args, **kwargs)

__all__ = ["create_app"]
