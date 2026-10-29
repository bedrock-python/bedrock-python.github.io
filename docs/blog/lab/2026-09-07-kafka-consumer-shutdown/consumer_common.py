"""Shared article code and the minimal servicewright container for this lab."""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-aiokafka-checklist"))
import kafka_flow as flow
from lab_support import committed_offset, fetch_count, infrastructure, seed


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self):
        return "1.0.0"


class Scope:
    async def get(self, key):
        raise KeyError(key)


class Container:
    @asynccontextmanager
    async def app_scope(self):
        yield Scope()

    @asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope()
