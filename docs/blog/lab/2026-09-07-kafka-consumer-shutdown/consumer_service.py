"""Wire the article's bounded consumer loop into servicewright."""

import os

# snippet:service
from servicewright import AppSpec, DaemonEntrypoint, Service, run_sync

from consumer_common import Container, Settings, flow


def build_service(bootstrap, process, *, group="tracking", grace=5):
    async def consume(scope, stop):
        # servicewright waits for this function; the shutdown bound is grace.
        await flow.run_tracking(bootstrap, process, stop, group=group, grace=grace)

    spec = AppSpec(
        service_name="tracking", create_container=lambda settings: Container(),
    )
    return Service(spec, entrypoints=[DaemonEntrypoint(consume)])
# /snippet:service


if __name__ == "__main__":
    view = flow.TrackingView()
    service = build_service(
        os.environ["KAFKA"], view.process, group=os.environ.get("GROUP", "tracking"),
    )
    run_sync(service, Settings())
