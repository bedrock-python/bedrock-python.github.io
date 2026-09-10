# Практикум: проверка здоровья Redis не ограничивается PING {#lab-redis-health-checks-ping-is-not-the-whole-story}

Скрипт запускает в одной сети три контейнера Redis 7: исправный основной узел, основной узел с `maxmemory 1mb` и `noeviction` и реплику первого. Для каждого выполняются штатная проверка здоровья библиотеки — PING — и пробная запись с последующим чтением. Затем основной узел приостанавливается.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "redis-client-kit[settings]==0.2.0" "testcontainers[redis]"
.venv/bin/python health_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-redis-health-checks).
