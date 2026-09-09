# Практикум: прогрев, готовность и жизнеспособность {#lab-warmup-readiness-and-liveness}

Сервис с трёхсекундным прогревом, проверкой готовности через Redis и маршрутом, который от них не зависит. Управляющий скрипт опрашивает `livez`, `readyz` и маршрут каждые 100 мс на протяжении всего жизненного цикла: прогрев, недоступность Redis через приостановку контейнера и `SIGTERM` с двухсекундной задержкой перед завершением приёма запросов. Выводятся все замеченные переходы.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi]==0.10.0" redis "httpx==0.28.1" "testcontainers[redis]"
.venv/bin/python driver.py
```

| Скрипт | Назначение |
|---|---|
| `service.py` | Сервис: прогрев, проверка готовности, один маршрут и пробы адаптера |
| `driver.py` | Redis в контейнере, опрос, приостановка и отправка сигнала |

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-warmup-readiness-liveness).
