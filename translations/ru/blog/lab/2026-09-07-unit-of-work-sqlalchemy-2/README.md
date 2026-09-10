# Практикум: Unit of Work в SQLAlchemy 2 {#lab-the-unit-of-work-in-sqlalchemy-2}

Один скрипт с PostgreSQL 17 в контейнере.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit==0.3.0" asyncpg "testcontainers[postgres]"
.venv/bin/python uow_lab.py
```

Пять сценариев: ошибка при второй записи, когда репозитории коммитят самостоятельно и когда используется Unit of Work; успешное выполнение того же сценария; запись внутри блока чтения; savepoint вокруг одного сбойного шага; модульный тест прикладного сценария без базы данных.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-unit-of-work-sqlalchemy-2).
