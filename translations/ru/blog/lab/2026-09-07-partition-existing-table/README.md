# Практикум: партиционирование работающей таблицы {#lab-partitioning-a-live-table}

`migrate_lab.py` запускает PostgreSQL 17 в контейнере, заполняет обычную таблицу `events` двумя миллионами строк за последний год и создаёт ссылающуюся на неё таблицу `event_notes`. Затем выполняет переход к месячным партициям, пока чтение и запись в `events` продолжаются: изменение ключа, подмена таблицы, первый цикл обслуживания, перенос данных пачками, внешний ключ и освобождение DEFAULT-партиции. Каждый шаг выводит свою длительность и результаты, которые видели читающий и пишущий процессы.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.1" asyncpg "testcontainers[postgres]"
.venv/bin/python migrate_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-partition-existing-table).
