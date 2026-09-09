---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - alembic-gauntlet
  - alembic
  - sqlalchemy
  - postgresql
  - migrations
  - testing
  - ci
  - testcontainers
---

# Пять тестов миграций, которые стоит запускать в CI каждого Python-проекта {#the-five-migration-tests-every-python-project-should-run-in-ci}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-five-alembic-migration-tests" role="img" aria-label="История ревизий проходит вперёд, назад и снова вперёд; по пути выполняются пять проверок" markdown="0"></div>

Мы тестируем приложение до зелёного значка покрытия, а затем развёртываем миграции БД, запущенные ровно один раз на ноутбуке в одну сторону. `downgrade()` впервые по-настоящему выполняется во время инцидента, руками дежурного, в production. Я решил проверить, какую часть риска снимут тесты: построил небольшую схему с четырьмя ревизиями, внедрил пять ошибок, которые сам выпускал, и прогнал три набора проверок — привычный для CI, пять самописных тестов через API Alembic и те же пять в библиотечном виде. Первый набор обнаружил одну ошибку из пяти.

<!-- more -->

Всё ниже запускалось на одном ноутбуке с PostgreSQL 17 в контейнере; код находится в [каталоге эксперимента](../lab/2026-09-07-five-alembic-migration-tests/README.md). Версии: Alembic 1.19.2, SQLAlchemy 2.0.52, asyncpg 0.31.0, testcontainers 4.15.0, pytest 9.1.1, pytest-asyncio 1.4.0, alembic-gauntlet 0.2.2, Python 3.13.

## Тест, который уже есть в большинстве CI {#the-test-most-pipelines-have}

Где-то в конфигурации CI запускается БД, выполняется `alembic upgrade head`, и работа продолжается. В виде теста это выглядит так:

```python
async def test_upgrade_head(migration_engine, alembic_config):
    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
```

Проверка доказывает, что миграции последовательно применяются к пустой БД. Это одно из требований к миграции. Вот что она показала для пяти ошибок:

| Ошибка | `upgrade head` |
|---|---|
| Откат забывает удалить созданный тип enum | пройден |
| Откат удаляет ограничение по несуществовавшему имени | пройден |
| Вручную изменённая миграция расходится с моделью по `NOT NULL` | пройден |
| Две ветки, две вершины, нет объединяющей ревизии | **ошибка** |
| Имя ограничения нарушает соглашение | пройден |

Четыре из пяти проходят. Единственная обнаруженная ошибка — Alembic сам отказывается выбирать одну из двух вершин. Остальные миграции применяются без проблем, оставаясь неверными.

## Пять ошибок, по одному файлу на каждую {#five-bugs-one-file-each}

Схема магазина: таблица `users`, таблица `orders` с внешним ключом, индексом и PostgreSQL enum для статуса, CHECK-ограничение суммы и добавленная позже колонка `is_active` у пользователей. Четыре ревизии в стиле autogenerate; соглашение об именах в metadata задаёт ограничениям имена, которые откат сможет найти:

```python
NAMING_CONVENTION = {
    "ix": "idx_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "chk_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```

Каждый ошибочный вариант — чистая история с изменением одного файла. Каждый случай я встречал в настоящем репозитории.

**Оставшийся enum.** Ревизия 0002 создаёт `orders` с колонкой `status` типа `order_status`. Откат удаляет таблицу, но не тип: `op.drop_table` о нём не знает. Откат проходит, следующее применение — нет.

**Опечатка в откате.** Ревизия 0003 добавляет CHECK-ограничение `amount_positive`, а откат удаляет `positive_amount`. Никто его не запускал, поэтому никто не знает об ошибке.

**Ручная правка.** Ревизия 0004 сгенерирована с `nullable=False` для `is_active`. Затем кто-то смягчил её до `nullable=True`, чтобы провести развёртывание, но модель не изменил. Модель утверждает одно, БД — другое, а ORM-запросы доверяют модели.

**Две вершины.** Ревизии 0003 и 0004 созданы в разных ветках от 0002 и слиты в один день. Каждая ветка локально работала. Вместе они дают две вершины, и `alembic upgrade head` отказывается запускаться.

**Имя вне соглашения.** Ревизия 0003 добавляет ограничение сырым SQL: `ALTER TABLE orders ADD CONSTRAINT amount_positive CHECK (amount > 0)`. Автор знал DDL и не стал искать вызов Alembic. Ограничение существует и работает, но единственное не следует соглашению. При будущем откате его имя придётся искать вручную.

## Пять тестов вручную {#five-tests-by-hand}

Каждому тесту нужны две вещи: собственная пустая схема и способ запустить Alembic на контролируемом тестом соединении. Схема создаётся через `CREATE SCHEMA` со случайным суффиксом и удаляется через `DROP SCHEMA ... CASCADE` в `finally`. Работа Alembic на переданном соединении требует контракта с `env.py`, к которому вернёмся ниже. С этими помощниками сами тесты короткие.

**Первый: каждую ревизию вперёд, назад и снова вперёд.** Это «лестница» — stairway. Она проходит от base до head и на каждом шаге применяет ревизию, откатывает на шаг и применяет снова:

```python
async def test_every_revision_up_down_up(migration_engine, alembic_config):
    revisions = revisions_base_to_head(alembic_config)
    async with fresh_schema(migration_engine) as schema:
        for i, revision in enumerate(revisions):
            await migrate(migration_engine, alembic_config, schema, command.upgrade, revision)
            assert await current_revision(migration_engine, schema) == revision
            await migrate(migration_engine, alembic_config, schema, command.downgrade, revisions[i - 1] if i else "base")
            await migrate(migration_engine, alembic_config, schema, command.upgrade, revision)
```

Важна третья строка внутри цикла. Откат, оставляющий лишний объект, проходит собственный шаг, но ломает следующее применение.

**Второй: схема соответствует моделям.** После полного обновления спрашиваем autogenerate, какие изменения он создал бы. Правильный ответ — никаких:

```python
async def test_schema_matches_the_models(migration_engine, alembic_config):
    def diff(conn):
        conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        ctx = MigrationContext.configure(conn, opts={"version_table_schema": schema})
        return [item for item in compare_metadata(ctx, Base.metadata) if not is_the_version_table(item)]

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(diff) == []
```

`compare_metadata` — функция, стоящая за `alembic revision --autogenerate`. Единственное допустимое отличие — таблица `alembic_version`, о которой модели не знают.

**Третий: ровно одна вершина.** База данных не нужна:

```python
def test_exactly_one_head(alembic_config):
    assert len(ScriptDirectory.from_config(alembic_config).get_heads()) == 1
```

**Четвёртый: откат до самого начала.** Репетируем аварийный откат: обновляемся до head, откатываемся до base и проверяем, что таблица версий подтверждает отсутствие применённых ревизий:

```python
async def test_downgrade_to_base(migration_engine, alembic_config):
    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        await migrate(migration_engine, alembic_config, schema, command.downgrade, "base")
        assert await current_revision(migration_engine, schema) is None
```

**Пятый: все имена следуют соглашению.** После полного обновления читаем из схемы все первичные, внешние, уникальные и CHECK-ограничения, а также индексы; сверяем имена с обещанными префиксами:

```python
NAME_RULES = {"pk": r"^pk_", "fk": r"^fk_", "uq": r"^uq_", "ck": r"^chk_", "ix": r"^idx_"}

async def test_names_follow_the_convention(migration_engine, alembic_config):
    def offenders(conn):
        insp = inspect(conn)
        bad = []
        for table in insp.get_table_names(schema=schema):
            if table == "alembic_version":
                continue
            named = [("pk", insp.get_pk_constraint(table, schema=schema)["name"])]
            named += [("fk", fk["name"]) for fk in insp.get_foreign_keys(table, schema=schema)]
            named += [("uq", uq["name"]) for uq in insp.get_unique_constraints(table, schema=schema)]
            named += [("ck", ck["name"]) for ck in insp.get_check_constraints(table, schema=schema)]
            named += [("ix", ix["name"]) for ix in insp.get_indexes(table, schema=schema) if not ix.get("duplicates_constraint")]
            bad += [f"{table}.{name}" for kind, name in named if not re.match(NAME_RULES[kind], name or "")]
        return bad

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(offenders) == []
```

Это похоже на наведение порядка, пока не вспомнишь, что откат — список имён для удаления. Если соглашение не задало имя объекта, следующему разработчику придётся искать его в `pg_constraint` перед написанием отката.

## Что обнаружил каждый тест {#what-each-test-caught}

Шесть запусков — по одному на каждую историю, включая обычное обновление:

| | чистая история | оставшийся enum | опечатка в откате | ручная правка | две вершины | имя вне соглашения |
|---|---|---|---|---|---|---|
| `upgrade head` | пройден | пройден | пройден | пройден | ОШИБКА | пройден |
| каждую ревизию вперёд, назад, вперёд | пройден | **ОШИБКА** | **ОШИБКА** | пройден | ОШИБКА | пройден |
| схема соответствует моделям | пройден | пройден | пройден | **ОШИБКА** | ОШИБКА | пройден |
| ровно одна вершина | пройден | пройден | пройден | пройден | **ОШИБКА** | пройден |
| полный откат | пройден | пройден | **ОШИБКА** | пройден | ОШИБКА | пройден |
| имена следуют соглашению | пройден | пройден | пройден | пройден | ОШИБКА | **ОШИБКА** |

Каждая ошибка обнаружена хотя бы одним тестом, а проверки дают разные гарантии: enum находит только лестница, ручную правку — только сравнение схемы, имя — только проверка соглашения. Две вершины ломают всё, что вызывает `upgrade head`; отдельный тест единственной вершины объясняет причину, а не только последствие.

Стоит прочитать сообщения: иначе читать их придётся в два часа ночи:

```text
enum left behind        asyncpg.exceptions.DuplicateObjectError: type "order_status" already exists
                        [SQL: CREATE TYPE order_status AS ENUM ('new', 'paid', 'shipped')]

typo in downgrade       asyncpg.exceptions.UndefinedObjectError: constraint "chk_orders_positive_amount"
                        of relation "orders" does not exist

hand edit               Database schema is out of sync with ORM models. Differences:
                        [('modify_nullable', None, 'users', 'is_active', {...}, True, False)]
                        Run: alembic revision --autogenerate

two heads               Found 2 head revisions; expected exactly 1. Merge branches with: alembic merge

name outside convention Check constraint 'amount_positive' on table 'orders' does not follow
                        naming conventions. Allowed prefixes: ['chk_'], suffixes: [].
```

Первые два сообщения выдаёт БД. В CI это неудачная проверка PR. В production первое означает откат, после которого нельзя обновиться снова, второе — откат, остановившийся на полпути.

## Чему меня научила проверка имён {#the-thing-the-naming-test-taught-me}

Посмотрите на сообщение об опечатке: миграция удаляла `positive_amount`, а БД жаловалась на `chk_orders_positive_amount`. Alembic применил соглашение к переданному имени. Если шаблон типа ограничения в metadata содержит `%(constraint_name)s`, аргумент `op.create_check_constraint` — не окончательное имя, а подставляемый фрагмент. `amount_positive` превращается в ожидаемое `chk_orders_amount_positive`. Но первая версия моей чистой истории передавала `"chk_orders_amount_positive"` и создавала `chk_orders_chk_orders_amount_positive`. Все тесты проходили: префикс был верным.

У autogenerate такой проблемы нет: он оборачивает имена в `op.f()`, помечая их окончательными. Рукописные миграции ошибиться могут, а сырой SQL вообще обходит соглашение — так возникла пятая ошибка. Из пяти тестов только проверка имён показывает, как объекты действительно называются в БД.

## Запуск в CI {#running-it-in-ci}

Нужен настоящий PostgreSQL. У SQLite нет схем, enum и такого же чтения ограничений; тест на другом движке проверяет другую миграцию. Самый доступный PostgreSQL — контейнер, запущенный один раз на тестовую сессию через session-scoped fixture:

```python
# tests/conftest.py
from alembic_gauntlet.contrib.testcontainers import migration_db_url  # noqa: F401
```

На ноутбуке с уже скачанным образом одиннадцать тестов эксперимента — обычное обновление, пять самописных и пять библиотечных — занимают 4,3 с, из которых 2,7 с уходит на старт контейнера. Лестница из четырёх ревизий занимает 0,4 с. Это вряд ли самая медленная часть CI. На Ubuntu runner GitHub есть Docker, поэтому тот же conftest работает без блока `services:`.

Две настройки обязательны. Тесты объявлены через `async def` без маркеров, поэтому pytest-asyncio должен работать в автоматическом режиме:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Engine должен использовать `NullPool`. Каждый тест задаёт `search_path` для соединения; соединение в пуле могло бы перенести эту настройку в следующий тест.

## Контракт с env.py {#the-contract-with-envpy}

Всё выше зависит от одной вещи, которую вы пишете сами: `env.py` должен работать на переданном тестом соединении в указанной тестом схеме. Alembic передаёт произвольные значения через `config.attributes`: это и есть канал:

```python
target_schema = config.attributes.get("target_schema") or os.getenv("MIGRATION_SCHEMA", "public")


def do_run_migrations(connection: Connection) -> None:
    if target_schema != "public":
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{target_schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{target_schema}"'))
    context.configure(connection=connection, target_metadata=target_metadata, version_table_schema=target_schema)
    with context.begin_transaction():
        context.run_migrations()


injected = config.attributes.get("connection")
if injected is not None:
    do_run_migrations(injected)
else:
    asyncio.run(run_migrations_online())
```

В production ничего не передаётся, выполняется ветка `else`, используется схема `public`. В тесте runner задаёт оба атрибута, открывает `engine.begin()` и вызывает `alembic.command.upgrade` на этом соединении. Все миграции выполняются внутри тестовой транзакции, в тестовой схеме и удаляются при очистке.

Именно `SET LOCAL`, а не `SET`. Обычный `SET search_path` переживает транзакцию и возвращается с соединением в пул. Запросы следующего получателя попадут в уже несуществующую схему. `SET LOCAL` действует до конца транзакции. Эту строку я проверил бы первой в любом `env.py` с изоляцией по схемам.

## Пять тестов одним импортом {#the-five-tests-as-one-import}

Пять самописных тестов с обвязкой занимают около восьмидесяти строк — одинаковых в каждом сервисе, где я работал. Одинаковая везде проверка просится в пакет. [alembic-gauntlet](https://bedrock-python.github.io/alembic-gauntlet/) предоставляет эти пять тестов как базовый класс:

```python
import pytest
from alembic_gauntlet import MigrationTestBase
from sqlalchemy import MetaData

from shop.models import Base


@pytest.mark.integration
class TestMigrations(MigrationTestBase):
    @pytest.fixture
    def orm_metadata(self) -> MetaData:
        return Base.metadata
```

От вас две fixture: URL базы и metadata. Конфигурация, engine, изолированная схема и пять тестов наследуются. В эксперименте оба набора прошли все шесть историй и упали в одних и тех же ячейках с приведёнными выше сообщениями. Правила имён читаются из `naming_convention` ваших metadata, поэтому поддерживать словарь `NAME_RULES` не нужно. Контракт с `env.py` остаётся описанным выше и остаётся вашей ответственностью.

Дело изначально было не в пакете, а в четырёх ячейках «пройден» в первой строке таблицы.
