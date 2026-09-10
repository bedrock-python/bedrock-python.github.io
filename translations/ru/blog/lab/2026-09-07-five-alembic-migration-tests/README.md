# Практикум: пять тестов миграций {#lab-the-five-migration-tests}

Код к [статье](../../posts/2026-09-07-five-alembic-migration-tests.md): история Alembic из четырёх ревизий для небольшого магазина, пять её вариантов с одной ошибкой в каждом и три набора тестов для каждого варианта. Нужен Docker; тестовая сессия сама запускает контейнер PostgreSQL 17.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "alembic-gauntlet[asyncio,testcontainers]==0.3.0" asyncpg
.venv/bin/python -m pytest -q                       # the clean history: 11 passed
VARIANT=drift .venv/bin/python -m pytest -q         # one buggy history
.venv/bin/python run_matrix.py                      # every suite against every history
VARIANTS=clean,drift,drift_server_default,drift_check_missing,drift_enum_value,drift_index_missing,drift_extra_column \
  .venv/bin/python run_matrix.py                    # the drift matrix
```

| Путь | Назначение |
|---|---|
| `shop/models.py` | ORM-модели: две таблицы, одно перечисление, соглашение об именовании |
| `migrations/env.py` | Контракт `env.py`: переданные извне соединение и схема, `SET LOCAL search_path` |
| `migrations/versions/clean/` | Четыре ревизии в том виде, в котором их создал бы autogenerate |
| `migrations/versions/<bug>/` | Те же ревизии с изменением одного файла; в `BUG.txt` указано, какого именно и что изменилось |
| `tests/test_plain_ci.py` | Типичная проверка в CI: `upgrade head` на пустой базе |
| `tests/test_by_hand.py` | Пять проверок через API Alembic; вспомогательный код — в `tests/helpers.py` |
| `tests/test_gauntlet.py` | Те же пять проверок, унаследованных от `alembic_gauntlet.MigrationTestBase`, плюс проверки check-ограничений и перечислений; сравнение серверных значений по умолчанию включено |
| `run_matrix.py` | Запуск набора тестов для каждого варианта и вывод матрицы результатов |
| `migrations/versions/drift_*/` | Шесть видов расхождений схемы для статьи: тип столбца, серверное значение по умолчанию, отсутствующий индекс, лишний столбец, отсутствующее check-ограничение и изменённое перечисление |
| `tests/test_drift_extras.py` | Три дополнительные проверки, написанные вручную до их появления в базовом классе |

Переменная окружения `VARIANT` выбирает каталог `migrations/versions/<variant>` через параметр Alembic `version_locations`; по умолчанию используется `clean`.

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-five-alembic-migration-tests).
