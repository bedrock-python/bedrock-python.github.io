"""This optional application path explicitly requires deadline-budget."""

from clientwright import AdapterDeps
from deadline_budget import BudgetContext
from http_flow import fetch_stock


async def fetch_with_budget(base_url):
    budget = BudgetContext.create(total_seconds=0.5)
    return await fetch_stock(base_url, AdapterDeps(deadline_source=budget))
