# Практикум: одного адреса недостаточно для пула каналов gRPC {#lab-grpc-channels-should-not-be-pooled-by-address-alone}

Один скрипт с сервером `grpc.aio` в том же процессе, который подсчитывает поступающие попытки.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-client-kit==0.1.0"
.venv/bin/python identity_lab.py
```

Три сценария: два клиента с разными цепочками интерсепторов обращаются к одному адресу через пул с ключом по адресу и через пул с ключом по полной идентичности канала; цепочка создаётся заново при каждом запросе и порождает новые каналы; один адрес используется с двумя конфигурациями keepalive. Число каналов берётся из внутренней таблицы пула — именно её поведение исследует практикум.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-grpc-channel-identity).
