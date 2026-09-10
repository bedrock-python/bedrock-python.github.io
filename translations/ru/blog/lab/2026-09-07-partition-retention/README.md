# Практикум: политика хранения партиций — это не DROP TABLE {#lab-partition-retention-is-not-drop-table}

Один скрипт с PostgreSQL 17 в контейнере. Он создаёт `events` с пятнадцатью месячными партициями, вручную присоединяет ещё одну с нестандартными границами и создаёт таблицу `receipts` с внешним ключом на `events`. Затем запускает типичную задачу очистки: `DROP TABLE` по шаблону имени, при ошибке — с `CASCADE`, и показывает, что осталось. Скрипт пересоздаёт таблицу и выполняет ту же очистку через план: вывод плана до изменений, отдельные этапы detach и drop с периодом ожидания, вызов архиватора перед удалением, включая его сбой, и обработка партиции, на которую ещё ссылается другая таблица.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.0" asyncpg "testcontainers[postgres]"
.venv/bin/python retention_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-partition-retention).
