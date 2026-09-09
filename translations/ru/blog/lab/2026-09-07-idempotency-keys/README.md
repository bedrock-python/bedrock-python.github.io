# Практикум: ключи идемпотентности {#lab-idempotency-keys}

Скрипт для измерения поведения идемпотентных запросов. Он сам запускает Redis 7 в контейнере.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]==0.3.0" "testcontainers[redis]"
.venv/bin/python measure.py
```

`measure.py` дважды вызывает списание с карты через координатор с одним ключом и интервалом 50 мс, пока первое списание ещё выполняется. Проверяются три режима обработки выполняющегося запроса. Затем скрипт повторно использует ключ с другой суммой, имитирует ошибку действия и направляет координатор на недоступный Redis.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-keys).
