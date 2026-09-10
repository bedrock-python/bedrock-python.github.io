# Практикум: одна доменная ошибка, два транспорта {#lab-one-domain-error-two-transports}

Один сервис с точками входа FastAPI и gRPC вызывает один и тот же прикладной сценарий. Он выбрасывает подклассы `ServiceError` и обычный `RuntimeError`; управляющий скрипт вызывает оба транспорта для каждого случая и выводит ответы клиенту.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi,grpc]==0.10.1" "httpx==0.28.1"
.venv/bin/python driver.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-transport-independent-errors).
