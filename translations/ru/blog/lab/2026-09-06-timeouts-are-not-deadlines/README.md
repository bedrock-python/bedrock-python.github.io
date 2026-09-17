# Практикум: таймауты — не дедлайны {#lab-timeouts-are-not-deadlines}

Скрипты, на которых основаны измерения [в статье](../../posts/2026-09-06-timeouts-are-not-deadlines.md).
Все серверы запускаются в том же процессе на loopback-интерфейсе; внешняя сеть нужна только для установки пакетов.
Из каталога практикума запустите скрипты с версиями, закреплёнными в `requirements.txt`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt 01_read_timeout.py
uv run --no-project --python 3.13 --with-requirements requirements.txt 02_retry_multiplies.py
uv run --no-project --python 3.13 --with-requirements requirements.txt 03_grpc_chain.py
uv run --no-project --python 3.13 --with-requirements requirements.txt 04_deadline_header.py
```

| Скрипт | Что измеряет |
|---|---|
| `01_read_timeout.py` | Поведение httpx с `timeout=1.0`: тело ответа поступает по частям четыре секунды; сервер задерживает заголовки; запрос выполняется внутри `asyncio.timeout` или с ограничением `total` в clientwright |
| `02_retry_multiplies.py` | Самописный цикл из трёх попыток обращения к серверу, который не отвечает, и те же попытки с единым общим лимитом времени |
| `03_grpc_chain.py` | Цепочку gateway → orders → inventory, billing: дедлайн на каждом сервере при отдельном таймауте каждого вызова и при передаче дедлайна шлюза; отдельно — бюджет 50 с при настроенном лимите вызова 5 с |
| `04_deadline_header.py` | Значение `X-Deadline-Ms`, которое получает вышестоящий HTTP-сервис при каждой попытке, если у вызывающей стороны есть общий бюджет запроса |

Время и значения заголовков зависят от планирования задач и установки соединений. HTTPX-адаптер в clientwright 0.2.2 выбрасывает `HttpxDeadlineExceededError`, который наследуется от `clientwright.DeadlineExceededError` и `httpx.TimeoutException`.

В gRPC-примере `asyncio.shield()` моделирует работу, уже принятую внешней платёжной системой. Она намеренно продолжается после отмены обработчика; это не утверждение о поведении всех записей в БД. Передача бюджета предотвращает запуск имитации списания при недостатке времени, но не отменяет уже выполненный резерв товара.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-06-timeouts-are-not-deadlines).
