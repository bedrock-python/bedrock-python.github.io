# Практикум: когда при сбое Redis стоит продолжать работу {#lab-when-should-redis-fail-open}

Два скрипта запускают Redis 7 в контейнере. Исчезновение Redis имитируется приостановкой контейнера: подключения не завершаются ни успехом, ни ошибкой — как при недоступном узле в сети.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "redis-client-kit[settings]" "idempotency-kit[redis]==0.3.0" "testcontainers[redis]"
.venv/bin/python retry_probe.py
.venv/bin/python fail_open_lab.py
```

`retry_probe.py` измеряет время одного GET к приостановленному Redis для каждой конфигурации клиента. `fail_open_lab.py` проверяет кэш, ограничитель частоты, координатор идемпотентности и проверку здоровья при работающем, приостановленном и восстановившемся Redis.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-when-should-redis-fail-open).
