# Практикум: что происходит, когда Kafka недоступна целый час {#lab-what-happens-when-kafka-is-down-for-an-hour}

Один скрипт сам запускает PostgreSQL 17 и Kafka в контейнерах. Недоступность Kafka имитируется приостановкой контейнера: брокер не отвечает и не отклоняет подключения.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "omni-box[postgres,kafka]==0.2.1" "testcontainers[kafka,postgres]" asyncpg
.venv/bin/python kafka_down_lab.py
```

Двадцать событий попадают в outbox, ещё три публикуются прямо из обработчика запроса через продюсер, подключённый до сбоя. Kafka приостанавливается, ретранслятор выполняет семь циклов, затем Kafka возвращается. Скрипт показывает статусы outbox и число сообщений в топике на каждом шаге. Весь прогон занимает пару минут, большая часть которых приходится на циклы с приостановленным брокером.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-when-kafka-is-down).
