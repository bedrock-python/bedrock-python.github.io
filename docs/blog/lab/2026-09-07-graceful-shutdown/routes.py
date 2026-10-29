"""Reuse the exact reports route and instrumented store from the shared lifecycle lab."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '2026-09-07-one-lifecycle'))
from one_lifecycle import Container, Settings, build_service, router
from report_store import ReportStore, open_store
