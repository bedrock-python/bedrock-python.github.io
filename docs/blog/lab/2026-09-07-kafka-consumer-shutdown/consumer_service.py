"""Wire the article's bounded consumer loop into servicewright."""

import os

# snippet:service
from servicewright import AppSpec, DaemonEntrypoint, Service, run_sync

from consumer_common import Container, Settings, flow


def build_service(bootstrap, process, *, group="tracking", grace=12):
    async def consume(scope, stop):
        # The timeout belongs to this loop. DaemonEntrypoint.drain() is a no-op.
        await flow.run_tracking(bootstrap, process, stop, group=group, grace=grace)

    spec = AppSpec(
        service_name="tracking", create_container=lambda settings: Container(),
        cleanup_timeout_seconds=3,
    )
    return Service(spec, entrypoints=[DaemonEntrypoint(consume)])
# /snippet:service


if __name__ == "__main__":
    view = flow.TrackingView()
    service = build_service(
        os.environ["KAFKA"], view.process, group=os.environ.get("GROUP", "tracking"),
    )
    run_sync(service, Settings())
