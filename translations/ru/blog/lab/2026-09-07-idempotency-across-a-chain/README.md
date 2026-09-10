# Практикум: идемпотентность в цепочке сервисов {#lab-idempotency-across-a-chain-of-services}

Три сервиса в одном процессе — шлюз, заказы и платежи. Каждый вызывает следующий по HTTP со своими повторными попытками; хранилище идемпотентности использует Redis в контейнере. Первая попытка всегда длится дольше таймаута вызывающей стороны: списание происходит, а ответ теряется. Сравниваются четыре подхода: без идемпотентности; новый ключ на каждую попытку; передача исходного ключа по всей цепочке; отсутствие заголовка, когда каждый сервис вычисляет ключ по отпечатку своего запроса.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]==0.3.0" "httpx==0.28.1" "testcontainers[redis]"
.venv/bin/python chain_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-across-a-chain).
