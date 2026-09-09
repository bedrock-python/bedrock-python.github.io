# Практикум: транзакционный режим PgBouncer и асинхронный SQLAlchemy {#lab-pgbouncer-transaction-mode-and-async-sqlalchemy}

Скрипты запускают PostgreSQL 17 и PgBouncer 1.25 в контейнерах одной сети Docker.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit[settings]==0.3.0" asyncpg "testcontainers[postgres]"
.venv/bin/python pgbouncer_lab.py
.venv/bin/python jit_probe.py
```

| Скрипт | Что измеряет |
|---|---|
| `pgbouncer_lab.py` | Двадцать клиентов дважды выполняют по двадцать разных запросов: напрямую к PostgreSQL, через PgBouncer с текущими настройками по умолчанию, через PgBouncer с `max_prepared_statements=0` и с настройками sqlalchemy-foundation-kit. В статье также приведены результаты версии 0.2.1 до исправления. Затем значение обычного `SET`, выполненного через одно клиентское соединение, читается через другое |
| `jit_probe.py` | Результаты `SHOW jit`, `SHOW search_path` и `SHOW application_name` через PgBouncer с `ignore_startup_parameters=jit,search_path` |

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-pgbouncer-async-sqlalchemy).
