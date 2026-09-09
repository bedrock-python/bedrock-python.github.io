# Практикум: однократные эффекты {#lab-exactly-once-effects}

Скрипт, на котором основаны измерения. Он сам запускает PostgreSQL 17 и Kafka в контейнерах.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "omni-box[postgres,kafka]==0.2.0" "testcontainers[kafka,postgres]" asyncpg
.venv/bin/python effects_lab.py
```

Четыре сценария: два окна сбоя при двойной записи — сначала commit, затем публикация и наоборот; сбой ретранслятора outbox после отправки с повторной публикацией в следующем цикле; получение обеих копий inbox-консьюмером, который создаёт счёт только один раз.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-exactly-once-effects).
