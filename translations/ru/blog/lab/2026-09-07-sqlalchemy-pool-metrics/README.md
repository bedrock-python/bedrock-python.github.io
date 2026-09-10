# Практикум: метрики пула соединений SQLAlchemy {#lab-what-to-monitor-in-a-sqlalchemy-connection-pool}

Скрипт с PostgreSQL 17 в контейнере: восемь воркеров, пул из двух соединений с двумя дополнительными overflow-соединениями, таймаут получения соединения в одну секунду и база, замедляющаяся в середине прогона. Метрики Prometheus из библиотеки снимаются каждые полсекунды: состояние пула, время ожидания соединения и время его удержания. Рядом выводится собственный счётчик неудачных получений соединения из приложения.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit[settings,metrics]==0.4.0" asyncpg "testcontainers[postgres]"
.venv/bin/python pool_metrics_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-sqlalchemy-pool-metrics).
