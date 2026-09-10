# Практикум: кто создаёт топик Kafka {#lab-who-creates-the-kafka-topic}

Один контейнер Kafka и шесть вопросов: что остаётся после записи продюсера в несуществующий топик; после подписки консьюмера на такой топик; что создаёт само приложение; что происходит, если следующий релиз запрашивает другую конфигурацию; как ведут себя три одновременно стартующие реплики; что происходит с запуском при настройках, которые кластер не может обеспечить.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "aiokafka-foundation-kit[models]==0.1.3" "testcontainers[kafka]"
.venv/bin/python topics_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-topics-on-startup).
