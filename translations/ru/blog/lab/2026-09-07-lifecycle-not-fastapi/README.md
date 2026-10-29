# Практикум: жизненный цикл приложения внутри FastAPI {#lab-why-application-lifecycle-should-not-belong-to-fastapi}

В `lifespan_api.py` хранилище отчётов открывается внутри FastAPI lifespan. В `lifespan_worker.py` запуск ресурса и прогрев настраиваются повторно для воркера. Обе версии корректно закрывают ресурс, в том числе при ошибке запуска. Общий runtime позволяет убрать это дублирование, когда у сервиса появляется несколько точек входа.

`check_lifespans.py` проверяет четыре случая: успешный HTTP-запрос, завершение отчёта в воркере и ошибку запуска в каждой версии. HTTP проверяется через `TestClient` FastAPI, воркер останавливается через `asyncio.Event`.

`ReportStore` взят из [практикума с общим жизненным циклом](../2026-09-07-one-lifecycle/README.md). Это имитация хранилища в памяти для проверки времени жизни ресурса, а не клиент базы данных. При копировании примеров сохраните соседний каталог практикума.

Запустите из каталога `docs/blog/lab/2026-09-07-lifecycle-not-fastapi` в копии репозитория:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python check_lifespans.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-lifecycle-not-fastapi).
