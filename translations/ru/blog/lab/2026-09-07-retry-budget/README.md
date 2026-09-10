# Практикум: повторные попытки могут усугубить сбой {#lab-retries-can-make-an-outage-worse}

Скрипт для измерения лавины повторных запросов к серверу clientwright в том же процессе.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2"
.venv/bin/python storm_lab.py
```

Четыре сценария: пятьдесят клиентов обращаются к серверу, который всегда отвечает 503, без повторов, с тремя попытками без бюджета и с бюджетом по умолчанию; те же пятьдесят клиентов при редких и частых временных сбоях; десять клиентов вызывают цепочку из трёх сервисов, где каждый повторяет запросы, без circuit breaker и бюджетов и с ними.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-retry-budget).
