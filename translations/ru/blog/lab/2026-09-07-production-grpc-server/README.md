# Практикум: устройство продакшен-сервера gRPC {#lab-the-anatomy-of-a-production-grpc-server}

Сервер `grpc.aio` в том же процессе собирается шестью способами, а клиент выводит результаты: что сообщается вызывающему коду при необработанном исключении; что видит интерсептор отчётности до и после обработчика исключений; какой ответ получает слишком большой запрос; что происходит с выполняющимся запросом при завершении сервера; что сообщает health-сервис при недоступной зависимости; какие подключения отклоняют TLS и mTLS. Сертификаты создаются через `openssl` во временном каталоге.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "grpc-server-kit[health,settings]==0.1.1"
.venv/bin/python server_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-production-grpc-server).
