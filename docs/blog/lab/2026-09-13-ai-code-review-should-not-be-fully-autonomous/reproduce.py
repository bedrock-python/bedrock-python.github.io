"""The same lost-reply invariant: fails before the fix and passes after it."""

import argparse
import asyncio

from reservation import ReservationOutcomeUnknown, reserve_once, reserve_with_retry
from warehouse_stub import WarehouseStub


async def check_lost_reply(reserve):
    warehouse = WarehouseStub("timeout_after_write", "ok")
    try:
        await reserve("order-42", warehouse)
    except ReservationOutcomeUnknown:
        pass
    print(f"calls={len(warehouse.calls)}, reservations={len(warehouse.reservations)}")
    assert len(warehouse.reservations) == 1, (
        "One operation created duplicate reservations"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("implementation", choices=("before", "after"))
    args = parser.parse_args()
    implementation = (
        reserve_with_retry if args.implementation == "before" else reserve_once
    )
    asyncio.run(check_lost_reply(implementation))
