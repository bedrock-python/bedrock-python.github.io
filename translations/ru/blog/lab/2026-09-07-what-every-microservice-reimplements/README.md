# Практикум: что заново реализует каждый Python-микросервис {#lab-what-every-production-python-microservice-reimplements}

`service.py` — сервис из ста строк из статьи: servicewright управляет жизненным циклом, sqlalchemy-foundation-kit — сессиями, clientwright — исходящим HTTP-клиентом, deadline-budget — дедлайном запроса. `run_skeleton.py` запускает PostgreSQL в контейнере, заглушку склада, которая сообщает полученный заголовок дедлайна, и сервис отдельным процессом. Затем вызывает сервис, отправляет SIGTERM и выводит хронологию.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "servicewright[fastapi,postgres]==0.10.0" "sqlalchemy-foundation-kit==0.2.1" \
  "clientwright[httpx,deadline]==0.2.2" "deadline-budget==0.1.3" asyncpg psycopg2-binary "testcontainers[postgres]"
.venv/bin/python run_skeleton.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-what-every-microservice-reimplements).
