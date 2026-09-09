# Практикум: подключение таблицы под управлением pg_partman {#lab-adopting-a-pg_partman-managed-table}

PostgreSQL 17 с pg_partman 5.5 запускается в контейнере из местного `Dockerfile`. pg_partman создаёт и обслуживает таблицу `events` с месячными партициями. Практикум читает её строку `part_config`, преобразует настройки в конфигурацию pg-partsmith и проверяет, что pg-partsmith видит в дереве, которое создал другой инструмент. Затем обслуживание последовательно выполняют оба инструмента; в конце pg_partman отключается и применяется отличающаяся политика.

```bash
docker build -t pg-partman-lab:17 .
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.1" asyncpg testcontainers
.venv/bin/python partman_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-migrating-from-pg-partman).
