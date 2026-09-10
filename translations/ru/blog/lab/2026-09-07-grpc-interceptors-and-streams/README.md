# Практикум: клиентские интерсепторы gRPC и потоковые RPC {#lab-grpc-client-interceptors-and-streaming-rpcs}

Сервер gRPC в том же процессе поддерживает все четыре вида RPC. Для клиентских интерсепторов проверяются одни и те же вопросы: для каких видов вызовов канал их зарегистрировал, какую длительность они измерили, заметили ли ошибку посреди потока, сохранялся ли их контекст во время получения элементов и какой объект в итоге получил вызывающий код.

- `interceptors_lab.py` — сравнение четырёх интерсепторов.
- `probe.py` — поведение `around_call`, который сохраняет токен `ContextVar` через `yield`, для каждого вида RPC.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-client-kit==0.1.2"
.venv/bin/python interceptors_lab.py
.venv/bin/python probe.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-grpc-interceptors-and-streams).
