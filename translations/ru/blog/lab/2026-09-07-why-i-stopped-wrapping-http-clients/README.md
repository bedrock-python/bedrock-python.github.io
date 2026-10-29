# Практикум: HTTP-клиенты, метрики и вложенные повторы {#lab-why-i-stopped-wrapping-http-clients}

`client_flow.py` содержит HTTP-фрагменты статьи. `http_origin.py` запускает локальный aiohttp-сервер с остатками, оплатой и управляемыми сбоями; `http_checks.py` содержит проверки, общие для пяти практикумов.

`wrappers_lab.py` проверяет сохранение интерфейсов HTTPX, aiohttp и Requests; один успешный вызов и три попытки при двух ответах 503 от склада; закрытие клиентов; отчёт о неподдерживаемом лимите попытки Requests через `inspect(client).report` и ошибку при `on_unsupported='strict'`; девять серверных запросов при трёх внешних повторах вокруг трёх попыток клиента.

Запросы проходят по настоящему HTTP на localhost. Requests вызывается в отдельном потоке, чтобы не блокировать асинхронный тестовый сервер. Примеры проверяют поведение, а не производительность транспорта.

Запустите из каталога `docs/blog/lab/2026-09-07-why-i-stopped-wrapping-http-clients` в копии репозитория. Версии зависимостей закреплены в `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python wrappers_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-why-i-stopped-wrapping-http-clients).
