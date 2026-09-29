"""Confirm the finding, the correction and the limits of the example."""

import unittest

from reservation import ReservationOutcomeUnknown, reserve_once, reserve_with_retry
from warehouse_stub import WarehouseStub


class ReviewEvidence(unittest.IsolatedAsyncioTestCase):
    async def test_original_success_path_has_one_reservation(self):
        warehouse = WarehouseStub("ok")
        result = await reserve_with_retry("order-42", warehouse)
        self.assertEqual(result["reservation_id"], "r-1")
        self.assertEqual(len(warehouse.reservations), 1)

    async def test_original_retry_duplicates_a_completed_operation(self):
        warehouse = WarehouseStub("timeout_after_write", "ok")
        result = await reserve_with_retry("order-42", warehouse)
        self.assertEqual(result["reservation_id"], "r-2")
        self.assertEqual(warehouse.calls, ["order-42", "order-42"])
        self.assertEqual(len(warehouse.reservations), 2)

    async def test_original_retry_is_bounded_even_when_both_replies_are_lost(self):
        warehouse = WarehouseStub("timeout_after_write", "timeout_after_write")
        with self.assertRaises(TimeoutError):
            await reserve_with_retry("order-42", warehouse)
        self.assertEqual(len(warehouse.calls), 2)
        self.assertEqual(len(warehouse.reservations), 2)

    async def test_fix_preserves_unknown_outcome_after_a_write(self):
        warehouse = WarehouseStub("timeout_after_write", "ok")
        with self.assertRaises(ReservationOutcomeUnknown) as caught:
            await reserve_once("order-42", warehouse)
        self.assertEqual(caught.exception.order_id, "order-42")
        self.assertIsInstance(caught.exception.__cause__, TimeoutError)
        self.assertEqual(len(warehouse.calls), 1)
        self.assertEqual(len(warehouse.reservations), 1)

    async def test_fix_also_reports_unknown_outcome_before_a_write(self):
        warehouse = WarehouseStub("timeout_before_write")
        with self.assertRaises(ReservationOutcomeUnknown):
            await reserve_once("order-42", warehouse)
        self.assertEqual(len(warehouse.calls), 1)
        self.assertEqual(warehouse.reservations, [])

    async def test_fix_keeps_the_success_result(self):
        warehouse = WarehouseStub("ok")
        result = await reserve_once("order-42", warehouse)
        self.assertEqual(result, {"reservation_id": "r-1", "order_id": "order-42"})
        self.assertEqual(len(warehouse.reservations), 1)

    async def test_fix_does_not_reclassify_other_errors(self):
        warehouse = WarehouseStub("denied")
        with self.assertRaises(PermissionError):
            await reserve_once("order-42", warehouse)
        self.assertEqual(len(warehouse.calls), 1)
        self.assertEqual(warehouse.reservations, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
