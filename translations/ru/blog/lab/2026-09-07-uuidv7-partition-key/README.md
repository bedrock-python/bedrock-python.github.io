# Практикум: UUIDv7 как ключ партиционирования PostgreSQL {#lab-uuidv7-as-a-postgresql-partition-key}

Скрипт с PostgreSQL 17 в контейнере: таблица с первичным ключом из одного столбца `UUID` и RANGE-партиционированием по нему. Границы месячных интервалов — минимальные UUIDv7 соответствующих месяцев. Скрипт выводит границы, распределяет строки с текущим временем и временем двухмесячной давности, сравнивает отсечение партиций по диапазону id и по столбцу времени. Затем проверяет неподходящие идентификаторы: импортированную историю, часы с опережением на три месяца, обычный uuid4 и запоздавшую строку за месяц, уже удалённый по политике хранения.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.0" asyncpg "testcontainers[postgres]"
.venv/bin/python uuidv7_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-uuidv7-partition-key).
