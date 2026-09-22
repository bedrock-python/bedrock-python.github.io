# Практикум: Переиспользование и изоляция gRPC-каналов {#lab-grpc-channels-should-not-be-pooled-by-address-alone}

Клиенты заказов и аудита обращаются по одному адресу склада. Сервер фиксирует три попытки клиента заказов и одну попытку аудита: правила повторов одного клиента не достались другому.

Через публичный `ChannelPool.get_channel()` проверяется переиспользование канала для постоянной цепочки перехватчиков и разделение каналов при другой цепочке, пересозданных перехватчиках или изменённых параметрах. После выхода из области пула полученные каналы сообщают `SHUTDOWN` через публичный API gRPC. Приватная таблица каналов не используется.

Сохраните соседний [практикум с повторами gRPC](../2026-09-07-safe-grpc-retries/README.md): здесь используются его stub, сервер и настройка приложения. Docker не нужен.

Запустите из каталога `docs/blog/lab/2026-09-07-grpc-channel-identity` в копии репозитория. Версии зависимостей закреплены в `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python identity_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-grpc-channel-identity).
