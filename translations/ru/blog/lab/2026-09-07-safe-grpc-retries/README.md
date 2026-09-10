# Практикум: безопасные повторы gRPC {#lab-safe-grpc-retries}

Скрипт для измерения повторных попыток. Сервер `grpc.aio` в том же процессе предоставляет метод `Charge`, поведение которого задаёт запрос: ошибка до списания, ошибка после него или медленный ответ. Сервер считает все списания. Поток `Export` при первой попытке обрывается на третьем элементе.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-client-kit[deadline]==0.1.0"
.venv/bin/python retries_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-safe-grpc-retries).
