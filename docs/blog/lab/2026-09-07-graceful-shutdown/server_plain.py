"""FastAPI under uvicorn, the way most services ship: uvicorn's own SIGTERM handling."""

import sys

import uvicorn
from fastapi import FastAPI

from routes import router

app = FastAPI()
app.include_router(router)


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    return {"status": "ready"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]), log_level="warning")
