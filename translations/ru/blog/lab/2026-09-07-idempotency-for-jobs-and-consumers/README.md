# Практикум: идемпотентность фоновых задач и консьюмеров {#lab-idempotency-for-background-jobs-and-consumers}

Один скрипт, который сам запускает Redis 7 в контейнере.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "idempotency-kit[redis]==0.3.0" "testcontainers[redis]"
.venv/bin/python jobs_lab.py
```

Три сценария: воркер падает после выполнения действия, но до подтверждения задания, с ключом идемпотентности и без него; два воркера одновременно обрабатывают одно задание в двух режимах обработки уже выполняющегося запроса; ключ строится по идентификатору доставки или самого действия либо содержит недопустимый символ.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-for-jobs-and-consumers).
