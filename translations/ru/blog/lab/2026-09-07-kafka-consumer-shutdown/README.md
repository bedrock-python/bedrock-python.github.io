# Практикум: корректное завершение консьюмера Kafka в Kubernetes {#lab-graceful-kafka-consumer-shutdown-in-kubernetes}

Два консьюмера с одинаковым циклом обработки и управляющий скрипт, имитирующий обновление каждого из них: запускает процесс, отправляет SIGTERM посреди пачки, запускает замену в той же группе и считает повторно обработанные сообщения и время ожидания первого сообщения новым консьюмером. Kafka запускается управляющим скриптом в контейнере.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "aiokafka-foundation-kit[models]==0.1.2" "servicewright==0.10.0" "testcontainers[kafka]"
.venv/bin/python driver.py
```

| Скрипт | Назначение |
|---|---|
| `consumer_common.py` | Настройки, топик и 200 мс «работы» на сообщение |
| `consumer_naive.py` | Цикл с commit после каждой пачки и немедленным выходом по SIGTERM |
| `consumer_service.py` | Тот же цикл под управлением servicewright: завершить пачку, зафиксировать смещения, выйти из группы |
| `driver.py` | Имитация обновления |

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-kafka-consumer-shutdown).
