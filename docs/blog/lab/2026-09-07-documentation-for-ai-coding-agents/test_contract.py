"""Test the documented API, example and failure cases against the pinned package."""

import ast
import asyncio
import inspect
import re
import unittest
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import deadline_budget.budget as budget_module
from deadline_budget import BudgetContext, DeadlineExceededError
from shipping import shipping_quote


class ManualClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class DocumentationContract(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.clock = ManualClock()
        self.clock_patch = patch.object(
            budget_module, "time", SimpleNamespace(monotonic=self.clock)
        )
        self.clock_patch.start()
        self.addCleanup(self.clock_patch.stop)

    def test_public_api_and_defaults(self):
        self.assertEqual(version("deadline-budget"), "0.1.3")
        create = inspect.signature(BudgetContext.create).parameters
        self.assertEqual(
            list(create), ["total_seconds", "call_caps", "min_timeout", "safety_margin"]
        )
        self.assertIsNone(create["call_caps"].default)
        self.assertEqual(create["min_timeout"].default, 0.1)
        self.assertEqual(create["safety_margin"].default, 0.0)
        self.assertEqual(create["min_timeout"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertFalse(inspect.iscoroutinefunction(BudgetContext.create))
        self.assertFalse(inspect.iscoroutinefunction(BudgetContext.timeout_for_call))

    async def test_awaiting_a_synchronous_method_is_an_error(self):
        with self.assertRaises(TypeError):
            await BudgetContext.create(total_seconds=0.6)

    def test_documented_code_matches_the_executed_module(self):
        root = Path(__file__).resolve().parent
        source = ast.parse((root / "shipping.py").read_text(encoding="utf-8"))
        source.body = source.body[
            1:
        ]  # The module docstring is not part of the snippet.
        snippets = re.findall(
            r"^```python\n(.*?)^```",
            (root / "README.md").read_text(encoding="utf-8"),
            re.MULTILINE | re.DOTALL,
        )
        self.assertEqual(len(snippets), 1)
        self.assertEqual(ast.dump(ast.parse(snippets[0])), ast.dump(source))

    async def test_sequential_steps_share_one_budget(self):
        calls = []

        async def stock(sku, *, timeout):
            calls.append(("stock", sku, timeout))
            self.clock.advance(0.25)
            return 3

        async def shipping(sku, *, timeout):
            calls.append(("shipping", sku, timeout))
            return {"shipping_cents": 490}

        result = await shipping_quote("sku-42", stock=stock, shipping=shipping)
        self.assertEqual(result, {"shipping_cents": 490})
        self.assertEqual(
            [(name, sku) for name, sku, _ in calls],
            [("stock", "sku-42"), ("shipping", "sku-42")],
        )
        self.assertAlmostEqual(calls[0][2], 0.4)
        self.assertAlmostEqual(calls[1][2], 0.35)

    async def test_no_stock_skips_shipping(self):
        async def stock(sku, *, timeout):
            return 0

        async def shipping(sku, *, timeout):
            self.fail("Shipping must not start for unavailable stock")

        self.assertIsNone(
            await shipping_quote("sku-42", stock=stock, shipping=shipping)
        )

    def test_minimum_can_exceed_remaining_time(self):
        default = BudgetContext.create(total_seconds=0.6)
        strict = BudgetContext.create(total_seconds=0.6, min_timeout=0)
        self.clock.advance(0.58)
        self.assertAlmostEqual(default.remaining(), 0.02)
        self.assertAlmostEqual(default.timeout_for_call("shipping"), 0.1)
        self.assertAlmostEqual(strict.timeout_for_call("shipping"), 0.02)

    def test_unknown_call_name_has_no_cap(self):
        ctx = BudgetContext.create(
            total_seconds=0.6, min_timeout=0, call_caps={"stock": 0.4}
        )
        self.assertAlmostEqual(ctx.timeout_for_call("stock"), 0.4)
        self.assertAlmostEqual(ctx.timeout_for_call("stcok"), 0.6)

    async def test_exhaustion_prevents_the_next_step(self):
        async def stock(sku, *, timeout):
            self.clock.advance(0.7)
            return 3

        async def shipping(sku, *, timeout):
            self.fail("Exhausted budget must prevent the next call")

        with self.assertRaises(DeadlineExceededError):
            await shipping_quote("sku-42", stock=stock, shipping=shipping)

    async def test_budget_alone_does_not_cancel_running_work(self):
        ctx = BudgetContext.create(total_seconds=0.6)
        released = asyncio.Event()
        task = asyncio.create_task(released.wait())
        try:
            await asyncio.sleep(0)
            self.clock.advance(0.7)
            self.assertTrue(ctx.expired())
            self.assertFalse(task.done())
            released.set()
            self.assertTrue(await asyncio.wait_for(task, timeout=1))
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def test_asyncio_timeout_cancels_a_stalled_step(self):
        cancelled = asyncio.Event()

        async def stock(sku, *, timeout):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        async def shipping(sku, *, timeout):
            self.fail("Shipping must not start after timeout")

        with self.assertRaises(TimeoutError):
            # An outer watchdog reports a broken example as a different error.
            task = asyncio.create_task(
                shipping_quote("sku-42", stock=stock, shipping=shipping)
            )
            done, _ = await asyncio.wait({task}, timeout=5)
            if task not in done:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
                self.fail("The example did not enforce its operation deadline")
            await task
        self.assertTrue(cancelled.is_set())

    async def test_dependency_timeout_is_not_budget_exhaustion(self):
        async def stock(sku, *, timeout):
            raise TimeoutError("Warehouse timed out")

        async def shipping(sku, *, timeout):
            self.fail("Shipping must not start after a failed stock call")

        with self.assertRaisesRegex(TimeoutError, "Warehouse timed out"):
            await shipping_quote("sku-42", stock=stock, shipping=shipping)


if __name__ == "__main__":
    unittest.main(verbosity=2)
