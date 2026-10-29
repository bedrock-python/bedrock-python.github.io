"""HTTP owns its startup and cleanup. The worker must wire the same resource separately."""
from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '2026-09-07-one-lifecycle'))
from report_store import ReportStore, open_store


def build_app(store):
    @asynccontextmanager
    async def lifespan(app):
        async with open_store(store):
            await store.ping()
            app.state.store = store
            yield

    app = FastAPI(lifespan=lifespan)

    @app.get('/reports')
    async def report():
        return await app.state.store.report('http')

    return app


if __name__ == '__main__':
    uvicorn.run(build_app(ReportStore()), host='127.0.0.1', port=8080)
