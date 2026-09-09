---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - alembic-gauntlet
  - alembic
  - testcontainers
  - postgresql
  - pytest
  - ci
---

# Тестирование миграций с Testcontainers: вперёд, назад и снова вперёд {#testing-database-migrations-with-testcontainers-up-down-and-up-again}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-testing-migrations-with-testcontainers" role="img" aria-label="Временная настоящая БД проходит обновление, откат и повторное обновление" markdown="0"></div>

[Статья о пяти тестах миграций](2026-09-07-five-alembic-migration-tests.md) объяснила, зачем они нужны. Здесь пошаговая настройка: от пустого `tests/` до зелёной задачи CI, проходящей каждую ревизию вперёд, назад и снова вперёд на настоящем PostgreSQL. Руководство короткое: сложная часть, контракт runner с `env.py`, занимает пятнадцать строк. Остальное — fixture и маркер. В конце — затраты времени на ноутбуке и условия запуска в GitHub Actions.

<!-- more -->

Код — [эксперимент статьи о пяти тестах](../lab/2026-09-07-five-alembic-migration-tests/README.md): четыре ревизии небольшого магазина и три набора проверок. Версии: Alembic 1.19.2, SQLAlchemy 2.0.52, asyncpg 0.31.0, testcontainers 4.15.0, pytest 9.1.1, pytest-asyncio 1.4.0, alembic-gauntlet 0.2.2, PostgreSQL 17, Python 3.13.

## Шаг 1: БД только на время тестовой сессии {#step-1-a-database-that-exists-only-for-the-test-session}

SQLite не заменяет PostgreSQL: нет схем, enum, иначе читаются ограничения. Другой движок проверяет другую миграцию. Самый простой настоящий PostgreSQL — контейнер на тестовую сессию, чья fixture возвращает DSN:

```python
# tests/conftest.py
from alembic_gauntlet.contrib.testcontainers import migration_db_url  # noqa: F401
```

Fixture запускает `postgres:17-alpine`, ждёт готовности и выдаёт URL подключения с драйвером asyncpg; в конце сессии контейнер останавливается. Если БД уже есть в compose разработчика или сервисах CI, переопределите fixture собственной session-scoped функцией с асинхронным DSN:

```python
@pytest.fixture(scope="session")
def migration_db_url() -> str:
    return "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
```

DSN обязан указывать async-драйвер. Обычный `postgresql://` выбирает psycopg2, который async engine отклонит до первого запроса.

## Шаг 2: настройка pytest {#step-2-pytest-configuration}

Две обязательные настройки:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
markers =
    integration: needs the PostgreSQL container
```

Тесты и fixture объявлены `async def` без отдельных маркеров, поэтому pytest-asyncio нужен режим auto. В strict появится «async def functions are not natively supported», а fixture вернут неожидаемые генераторы. Маркер позволяет запускать модульные тесты без Docker через `pytest -m "not integration"`.

## Шаг 3: контракт с env.py {#step-3-the-contract-with-envpy}

Runner не запускает команду `alembic` через оболочку. Он вызывает `alembic.command.upgrade` и `downgrade` в процессе на собственном соединении, в контролируемой транзакции и специально созданной схеме. Для этого `env.py` обязан использовать переданные значения:

```python
target_schema = config.attributes.get("target_schema") or os.getenv("MIGRATION_SCHEMA", "public")


def do_run_migrations(connection: Connection) -> None:
    if target_schema != "public":
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{target_schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{target_schema}"'))  # LOCAL: dies with the transaction
    context.configure(connection=connection, target_metadata=target_metadata, version_table_schema=target_schema)
    with context.begin_transaction():
        context.run_migrations()


injected = config.attributes.get("connection")
if injected is not None:
    do_run_migrations(injected)          # the test runner owns the connection and the transaction
else:
    asyncio.run(run_migrations_online())  # production: build the engine from the URL
```

Перед каждой командой runner задаёт `connection` и `target_schema`, после удаляет. В production их нет, работает прежняя ветка `else`. Критична строка `SET LOCAL`: обычный `SET search_path` переживает транзакцию и возвращается с соединением в пул, направляя следующий тест в уже удалённую схему.

## Шаг 4: файл тестов {#step-4-the-test-file}

```python
# tests/test_migrations.py
import pytest
from alembic.config import Config
from alembic_gauntlet import MigrationTestBase
from sqlalchemy import MetaData

from shop.models import Base


@pytest.mark.integration
class TestMigrations(MigrationTestBase):
    @pytest.fixture
    def orm_metadata(self) -> MetaData:
        return Base.metadata

    @pytest.fixture
    def alembic_config(self) -> Config:      # only if alembic.ini is not in the working directory
        return Config("alembic.ini")
```

Наследование базового класса даёт пять тестов: каждая ревизия вперёд, на шаг назад и снова вперёд; сравнение итоговой схемы с моделями через autogenerate; одна вершина; полный откат до base; имена ограничений и индексов по соглашению metadata. У каждого теста своя схема `test_mig_<hex>`, удаляемая с `CASCADE` после выполнения. Поэтому возможен параллельный запуск через `pytest -n auto`.

Главный цикл лестницы в явном виде:

```python
for i, revision in enumerate(revisions):            # base -> head
    upgrade(revision)
    assert current_revision() == revision
    downgrade(revisions[i - 1] if i else "base")
    upgrade(revision)                                # a downgrade that left something behind fails here
```

## Шаг 5: CI {#step-5-ci}

На Ubuntu runner GitHub есть Docker, поэтому тот же conftest работает без `services:`:

```yaml
test-integration:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
    - uses: astral-sh/setup-uv@v7
    - run: uv sync --group dev
    - run: uv run pytest -m integration
```

Если вместо Testcontainers используется заранее предоставленная БД, например сервис PostgreSQL в поддерживающем его CI, подходит переопределение fixture из первого шага.

## Затраты времени {#what-it-costs}

На ноутбуке с уже скачанным образом одиннадцать тестов — обычное обновление, пять самописных и пять унаследованных — занимают 4,3 с. Из них 2,7 с — старт контейнера, 0,4 с — лестница четырёх ревизий. Для сорока сходных по стоимости ревизий ожидается примерно десятикратная стоимость лестницы при прежнем контейнере, то есть менее десяти секунд; тяжёлые миграции нужно измерять отдельно. В исходном эксперименте все пять ошибок обнаружены за этот бюджет. Без набора проверок обычный `alembic upgrade head` нашёл бы только две вершины.

Базовый класс предоставляет [alembic-gauntlet](https://bedrock-python.github.io/alembic-gauntlet/guide/quickstart/), контракту с `env.py` посвящена [отдельная страница](https://bedrock-python.github.io/alembic-gauntlet/guide/env-py/).

Суть — в третьем шаге: пятнадцать строк и `SET LOCAL`.
