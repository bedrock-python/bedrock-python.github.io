# Практикум: единый жизненный цикл для HTTP, планировщика и воркера {#lab-one-lifecycle-for-http-a-scheduler-and-a-worker}

`one_lifecycle.py` задаёт один `AppSpec` с тремя точками входа — сервером FastAPI, заданием APScheduler каждые полсекунды и фоновым циклом, — которые используют общий пул. `ROLE` определяет, какие из них запускает процесс. Каждая точка входа обёрнута трассировщиком, печатающим четыре вызова со стороны Host. `run_roles.py` запускает сервис в режимах `all`, `api` и `worker`, ненадолго создаёт нагрузку, отправляет SIGTERM и выводит хронологию.

```bash
uv venv --python 3.13 .venv
uv pip install --prerelease=allow --python .venv/bin/python "servicewright[fastapi,apscheduler4]==0.10.0" "httpx==0.28.1"
.venv/bin/python run_roles.py
```

`--prerelease=allow` нужен для предварительной версии APScheduler 4. Зафиксируйте версию httpx, иначе этот же флаг разрешит установить разрабатываемую версию 1.0.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-one-lifecycle).
