"""Run the article's wrappers checks against real local HTTP."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '2026-09-07-why-i-stopped-wrapping-http-clients'))
from http_checks import wrappers, run

if __name__ == '__main__':
    run(wrappers)
