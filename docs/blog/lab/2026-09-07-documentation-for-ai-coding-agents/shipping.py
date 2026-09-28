"""Application example for a compact, executable documentation contract."""

import asyncio

from deadline_budget import BudgetContext


async def shipping_quote(sku, *, stock, shipping):
    ctx = BudgetContext.create(
        total_seconds=0.6,
        min_timeout=0,
        call_caps={"stock": 0.4, "shipping": 0.4},
    )
    async with asyncio.timeout(ctx.remaining()):
        available = await stock(sku, timeout=ctx.timeout_for_call("stock"))
        if available <= 0:
            return None
        return await shipping(sku, timeout=ctx.timeout_for_call("shipping"))
