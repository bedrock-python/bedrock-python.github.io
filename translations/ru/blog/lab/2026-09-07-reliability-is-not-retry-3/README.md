# Практикум: надёжность — это не retry=3 {#lab-reliability-is-not-retry3}

Один сервер в том же процессе и сорок параллельных клиентов в шести конфигурациях: без повторов, `retry=3`, повторы с дедлайном в одну секунду, повторы с бюджетом попыток, повторы с circuit breaker для origin и две волны через один клиент, чтобы breaker успел увидеть ошибки. Для каждой конфигурации измеряются число запросов к серверу, число обслуженных клиентов, максимальное время ожидания и задержка первого успешного запроса после восстановления сервера.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2" "httpx==0.28.1"
.venv/bin/python reliability_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-reliability-is-not-retry-3).
