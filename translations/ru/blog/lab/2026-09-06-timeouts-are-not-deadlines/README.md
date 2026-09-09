# Практикум: таймауты — не дедлайны {#lab-timeouts-are-not-deadlines}

Скрипты, на которых основаны измерения [в статье](../../posts/2026-09-06-timeouts-are-not-deadlines.md).
Все серверы запускаются в том же процессе на loopback-интерфейсе; внешняя сеть не нужна.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "deadline-budget==0.1.3" "clientwright[httpx,deadline]==0.2.2" "grpc-client-kit[deadline]==0.1.0"
.venv/bin/python 01_read_timeout.py
.venv/bin/python 02_retry_multiplies.py
.venv/bin/python 03_grpc_chain.py
.venv/bin/python 04_deadline_header.py
```

| Скрипт | Что измеряет |
|---|---|
| `01_read_timeout.py` | Поведение httpx с `timeout=1.0`: тело ответа поступает по частям четыре секунды; сервер задерживает заголовки; запрос выполняется внутри `asyncio.timeout` или с ограничением `total` в clientwright |
| `02_retry_multiplies.py` | Самописный цикл из трёх попыток обращения к серверу, который не отвечает, и те же попытки с единым общим лимитом времени |
| `03_grpc_chain.py` | Цепочку gateway → orders → inventory, billing: дедлайн на каждом сервере при отдельном таймауте каждого вызова и при передаче дедлайна шлюза; отдельно — бюджет 50 с при настроенном лимите вызова 5 с |
| `04_deadline_header.py` | Значение `X-Deadline-Ms`, которое получает вышестоящий HTTP-сервис при каждой попытке, если у вызывающей стороны есть общий бюджет запроса |

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-06-timeouts-are-not-deadlines).
