# Практикум: отдельный circuit breaker для каждого origin {#lab-circuit-breakers-should-be-per-origin}

Один скрипт и три сервера в том же процессе.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2"
.venv/bin/python breakers_lab.py
```

Четыре сценария: один клиент обращается к трём сервисам, один из которых недоступен, с самописным circuit breaker на уровне клиента и с отдельным breaker для каждого origin; какие ответы размыкают цепь; подсчёт отдельных попыток и логических вызовов при повторных запросах; пробный запрос в состоянии half-open после истечения времени восстановления.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-circuit-breakers-per-origin).
