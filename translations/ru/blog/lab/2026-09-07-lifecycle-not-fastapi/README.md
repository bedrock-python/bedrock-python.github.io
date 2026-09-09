# Практикум: почему жизненный цикл приложения не должен принадлежать FastAPI {#lab-why-application-lifecycle-should-not-belong-to-fastapi}

Часть статьи «до»: `lifespan_api.py` хранит жизненный цикл в lifespan FastAPI, а `lifespan_worker.py` содержит воркер того же сервиса, у которого нет lifespan и которому приходится повторять служебный код. Часть «после» — [практикум с единым жизненным циклом](../2026-09-07-one-lifecycle/), где API, планировщик и воркер используют один `AppSpec`.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python fastapi "uvicorn[standard]"
.venv/bin/python lifespan_api.py 8000        # then SIGTERM it
.venv/bin/python lifespan_worker.py          # then SIGTERM it
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-lifecycle-not-fastapi).
