"""Manual entrypoint: servicewright owns signals and the shared resource."""
from routes import Settings, build_service
from servicewright import run_sync


if __name__ == '__main__':
    service, _, _ = build_service('api')
    run_sync(service, Settings())
