# Практикум: транзакционный inbox {#lab-the-transactional-inbox}

Один скрипт, который сам запускает PostgreSQL 17 и Kafka в контейнерах.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "omni-box[postgres,kafka]==0.2.0" "testcontainers[kafka,postgres]" asyncpg
.venv/bin/python inbox_lab.py
```

Для каждой стратегии подтверждения проверяются одно сообщение и обработчик, который создаёт счёт и падает при первом запуске. Затем запускается новый консьюмер той же группы и проверяется, что он получает. Сценарий повторной доставки находится в [практикуме об однократных эффектах](../2026-09-07-exactly-once-effects/).

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-transactional-inbox).
