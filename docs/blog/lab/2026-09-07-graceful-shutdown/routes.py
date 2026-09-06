"""The same two routes for every server: a quick request and a slow one."""

import asyncio

from fastapi import APIRouter

router = APIRouter()


@router.get("/work")
async def work() -> dict[str, str]:
    await asyncio.sleep(0.02)
    return {"status": "ok"}


@router.get("/slow")
async def slow() -> dict[str, str]:
    await asyncio.sleep(2.0)  # a report, an export, a payment: in flight when the signal lands
    return {"status": "done"}
