# Практикум: почему я перестал оборачивать HTTP-клиенты {#lab-why-i-stopped-wrapping-http-clients}

Скрипт для измерений с сервером clientwright, который работает в том же процессе и имитирует сбои.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "clientwright[httpx,aiohttp,requests]==0.2.2" tenacity
.venv/bin/python wrappers_lab.py
```

Четыре сценария: тип клиента, возвращаемого каждым `build()`; одна политика повторов для httpx и aiohttp при двух ошибках подряд и метрики каждого клиента; цикл tenacity вокруг клиента, который уже повторяет запросы; сообщения сборки, когда адаптер не поддерживает настройку, в режимах `warn` и `strict`.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-why-i-stopped-wrapping-http-clients).
