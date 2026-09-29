"""Controlled failure points, not a network client or production warehouse."""


class WarehouseStub:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.reservations = []

    async def reserve(self, order_id):
        self.calls.append(order_id)
        outcome = self.outcomes.pop(0) if self.outcomes else "ok"
        if outcome == "timeout_before_write":
            raise TimeoutError("Request failed before the reservation was created")
        if outcome == "denied":
            raise PermissionError("Reservation is not allowed")
        reservation = {
            "reservation_id": f"r-{len(self.reservations) + 1}",
            "order_id": order_id,
        }
        self.reservations.append(reservation)
        if outcome == "timeout_after_write":
            raise TimeoutError("Reservation was created, but its reply was lost")
        if outcome != "ok":
            raise ValueError(f"Unknown fixture outcome: {outcome}")
        return reservation
