# Практикум: корректное завершение — это протокол {#lab-graceful-shutdown-is-a-protocol}

Скрипты для измерения завершения работы: два сервера с одинаковыми маршрутами и управляющий скрипт, имитирующий поведение Kubernetes.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi]" httpx
.venv/bin/python driver.py server_plain.py
.venv/bin/python driver.py server_servicewright.py                  # drain_delay_seconds=0
DRAIN_DELAY=1.5 .venv/bin/python driver.py server_servicewright.py  # the protocol with its window
```

| Скрипт | Назначение |
|---|---|
| `routes.py` | Общие для обоих серверов маршруты `/work` (20 мс) и `/slow` (2 с) |
| `server_plain.py` | FastAPI под `uvicorn.run` со штатной обработкой SIGTERM в uvicorn |
| `server_servicewright.py` | Те же маршруты под управлением жизненного цикла servicewright; `DRAIN_DELAY` задаёт `AppSpec.drain_delay_seconds` |
| `driver.py` | Запускает сервер, ждёт готовности, отправляет один медленный запрос и SIGTERM, затем продолжает отправлять запросы каждые 20 мс в течение `LAG` секунд — задержки распространения изменений endpoints, — опрашивает readiness и подсчитывает ответы |

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-graceful-shutdown).
