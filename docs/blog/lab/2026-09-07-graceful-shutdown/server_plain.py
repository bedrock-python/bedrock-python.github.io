"""An HTTP-only alternative: FastAPI lifespan owns the resource, Uvicorn drains requests."""
from contextlib import asynccontextmanager
import sys
import uvicorn
from fastapi import FastAPI
from routes import ReportStore, open_store


def build_app(store):
    @asynccontextmanager
    async def lifespan(app):
        async with open_store(store):
            await store.ping()
            yield

    app = FastAPI(lifespan=lifespan)

    @app.get('/reports')
    async def report():
        return await store.report('http')

    return app


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    uvicorn.run(build_app(ReportStore()), host='127.0.0.1', port=port)
