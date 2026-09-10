# Практикум: Retry-After, backoff и jitter {#lab-retry-after-backoff-and-jitter}

Один скрипт и сервер clientwright в том же процессе.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx]==0.2.2"
.venv/bin/python backoff_lab.py
```

Четыре сценария: ответ `503` с учётом и игнорированием заголовка `Retry-After`; моменты повторных запросов от пятидесяти клиентов с jitter и без него; число полученных сервером POST-запросов после таймаута чтения, когда операция объявлена идемпотентной и когда не объявлена; результаты и HTTP-методы, для которых повторы разрешены по умолчанию.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-retry-after-backoff-jitter).
