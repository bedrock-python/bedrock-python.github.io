# Lab: why application lifecycle should not belong to FastAPI

The "before" half of the post: `lifespan_api.py` keeps the lifecycle in FastAPI's lifespan, and
`lifespan_worker.py` is the worker for the same service, which has no lifespan and writes the same
plumbing again. The "after" half is [the one-lifecycle lab](../2026-09-07-one-lifecycle/), where the
API, a scheduler and the worker share one `AppSpec`.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python fastapi "uvicorn[standard]"
.venv/bin/python lifespan_api.py 8000        # then SIGTERM it
.venv/bin/python lifespan_worker.py          # then SIGTERM it
```
