# Практикум: кто владеет сессией {#lab-who-owns-the-session}

Один сценарий «оформить заказ» реализован четырьмя способами с PostgreSQL 17 в контейнере: отдельная сессия на репозиторий; общая сессия, которую коммитит репозиторий; единый Unit of Work; Unit of Work с savepoint. Во всех вариантах запись в outbox падает, а практикум считает сохранившиеся данные. Затем те же подходы проверяются с пулом из двух соединений, одна сессия передаётся двум задачам, а транзакция используется после выхода из её блока.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit==0.3.0" "testcontainers[postgres]"
.venv/bin/python sessions_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-stop-passing-asyncsession-everywhere).
