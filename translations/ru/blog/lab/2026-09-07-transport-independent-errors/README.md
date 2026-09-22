# Практикум: одна доменная ошибка, два транспорта {#lab-one-domain-error-two-transports}

Servicewright запускает HTTP и gRPC в одном процессе на портах, выбранных ОС. Оба обработчика вызывают одну функцию получения счёта. Управляющий скрипт отправляет настоящие сетевые запросы, сравнивает успешные ответы и проверяет семь ошибок через оба транспорта.

HTTP возвращает `application/problem+json`, а gRPC передаёт тот же прикладной код через trailing metadata `x-error-code`. Неоплаченный заказ имеет категорию `PRECONDITION_FAILED`: HTTP 412 и gRPC `FAILED_PRECONDITION`. Закрытые ошибки и неожиданные исключения превращаются в `internal_error`; внутренние сообщения, параметры и закрытые коды не должны попасть в ответ.

Скрипт останавливает сервис через событие остановки и проверяет, что общее хранилище закрывается после завершения обеих точек входа. Хранилище работает в памяти. Покупатель задан доверенными тестовыми данными; аутентификация в этом практикуме не реализована.

Нужен `uv`. Запустите из каталога `docs/blog/lab/2026-09-07-transport-independent-errors`:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python driver.py
```

Версии закреплены в `requirements.txt`: grpc-server-kit 0.2.0, servicewright 0.13.1, grpcio 1.84.0, FastAPI 0.141.1, Uvicorn 0.53.0, HTTPX 0.28.1 и cryptography 50.0.1.

Сохраните соседний каталог `2026-09-07-production-grpc-server`: практикум использует его прикладной код, имитаторы и зависимости.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-transport-independent-errors).
