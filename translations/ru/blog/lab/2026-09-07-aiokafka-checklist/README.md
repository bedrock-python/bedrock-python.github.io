# Практикум: проверка aiokafka перед продакшеном {#lab-the-production-checklist-for-aiokafka}

Один контейнер Kafka и скрипты для проверки каждого вопроса: с какими настройками продюсер отказывается создаваться, как работают сериализаторы значения и ключа, что перечитывает новый консьюмер, какие смещения фиксирует auto-commit, что происходит при обработке пачки дольше `max_poll_interval_ms`, как создаются топики и сколько стоит проверка здоровья при приостановленном брокере.

- `checklist_lab.py` — проверка по разделам статьи.
- `topic_probe.py` — проверка того, может ли `ensure_topics_async` вообще создать топик.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "aiokafka-foundation-kit[models]==0.1.3" "testcontainers[kafka]"
.venv/bin/python checklist_lab.py
.venv/bin/python topic_probe.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-aiokafka-checklist).
