---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - alembic-gauntlet
  - alembic
  - sqlalchemy
  - postgresql
  - migrations
  - ci
---

# Модели и схема БД разошлись. Заметит ли CI? {#your-models-and-your-schema-have-drifted-would-ci-notice}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-your-models-and-your-schema-have-drifted" role="img" aria-label="Два описания, которые должны совпадать, расходятся там, где не было проверки" markdown="0"></div>

Миграция прошла, развёртывание завершилось, модели и БД теперь утверждают разное. Ошибки нет: обычный `alembic upgrade head` на пустой БД не проверяет соответствие результата моделям. Я создал шесть расхождений, каждое правкой одной ревизии, и прогнал три набора тестов. Обычный CI не обнаружил ни одного, стандартное сравнение autogenerate — три. Для остальных нужны дополнительные настройки и проверки.

<!-- more -->

Числа получены в [эксперименте статьи](../lab/2026-09-07-five-alembic-migration-tests/README.md) с PostgreSQL 17 в контейнере. Версии: alembic-gauntlet 0.3.0, Alembic 1.19.2, SQLAlchemy 2.0.52, Python 3.13.

## Откуда берутся расхождения {#where-drift-comes-from}

Обычно никто не создаёт их намеренно. Три пути:

**Ручная правка миграции.** Autogenerate создал ревизию, человек изменил её: переименование представлено как удаление и создание либо `ALTER` слишком долго блокирует таблицу. SQL корректен, но уже не равен модели.

**Срочное исправление production.** Индекс создан вручную в три часа ночи для остановки инцидента. В миграциях его нет. Сравнение моделей с такой БД позже может предложить удалить индекс как лишний.

**Непроверяемые свойства.** Самый незаметный источник. Alembic сравнивает таблицы, колонки, типы, nullable и индексы, но не всё содержимое CHECK и enum. Server defaults по умолчанию не сравниваются без включения.

## Шесть расхождений {#the-six-drifts}

Шесть историй, каждая отличается от чистой одной ревизией:

| Вариант | Ревизия | Расхождение |
|---|---|---|
| `drift` | `0004` разрешает NULL в `is_active` | Модель требует `NOT NULL` |
| `drift_server_default` | `0004` задаёт `server_default false` | В модели `true` |
| `drift_index_missing` | `0002` не создаёт индекс | У колонки модели `index=True` |
| `drift_extra_column` | `0001` добавляет необъявленную колонку | В БД колонка без модели |
| `drift_check_missing` | `0003` не создаёт CHECK | Модель требует `amount > 0` |
| `drift_enum_value` | `0002` создаёт enum без `shipped` | В модели три значения |

Каждую проверяют обычный `upgrade head`, пять самописных тестов API Alembic и те же унаследованные проверки с двумя дополнительными проверками базового класса.

```text
                                    clean     drift  server_default  check_missing  enum_value  index_missing  extra_column
test_upgrade_head                    pass      pass       pass           pass          pass         pass          pass
test_every_revision_up_down_up       pass      pass       pass           pass          pass         pass          pass
test_schema_matches_the_models       pass      FAIL       pass           pass          pass         FAIL          FAIL
test_migrations_up_to_date           pass      FAIL       FAIL           pass          pass         FAIL          FAIL
test_check_constraints_match         pass      pass       pass           FAIL          pass         pass          pass
test_enum_values_match               pass      pass       pass           pass          FAIL         pass          pass
test_downgrade_to_base               pass      pass       pass           pass          pass         pass          pass
test_exactly_one_head                pass      pass       pass           pass          pass         pass          pass
test_names_follow_the_convention     pass      pass       pass           pass          pass         pass          pass
```

Первая строка — весь аргумент. `alembic upgrade head` успешен при каждом расхождении: SQL валиден и применяется. Проверку того, что миграции *выполняются*, ошибочно принимают за доказательство *правильности* схемы.

## Проверка, ловящая половину {#the-check-that-catches-half-of-them}

Четыре строки: обновить свежую БД до head, сравнить с моделями через autogenerate, считать любой diff ошибкой.

```python
context = MigrationContext.configure(connection, opts={"compare_server_default": True})
differences = compare_metadata(context, Base.metadata)
assert not differences
```

`test_migrations_up_to_date` отличает «запускается» от «создаёт ожидаемую кодом схему». В эксперименте находит изменение nullable, отсутствующий индекс и лишнюю колонку, показывая расхождение:

```text
AssertionError: Database schema is out of sync with ORM models. Differences:
  [[('modify_nullable', None, 'users', 'is_active', {...}, True, False)]]
  Run: alembic revision --autogenerate
```

Сообщение одновременно подсказывает исправление: именно такой diff autogenerate предложил бы для следующей ревизии.

## Что нужно включить отдельно {#the-one-it-will-not-look-at-unless-you-ask}

`drift_server_default` интересен сочетанием pass и FAIL у одной проверки. Тот же набор, та же история:

```text
    migration_diff_compare_server_default left at its default:  7 passed
    the same suite with it set to True:                         1 failed
```

Alembic не сравнивает server defaults по умолчанию намеренно. PostgreSQL нормализует выражения: `server_default="true"`, `sa.text("now()")`, числовые `0` и `0.0` могут иметь другое текстовое представление. Наивное сравнение создаёт ложные различия, и шумную проверку со временем отключают.

Поэтому включение требует внимания. Возможны уточнения записи или функции сравнения defaults. Без него `false` в миграции против `true` в модели незаметны. Мой подход — включить и разбирать различия представления, а не отключать всю проверку.

## Чего стандартное сравнение не видит {#the-two-it-will-never-look-at}

Последние два случая не решаются обычным флагом autogenerate. Проверяемая стандартная конфигурация не сравнивает CHECK и значения enum, поэтому повторная генерация может быть пустой. Она честно сообщает только об исследованном.

Чтение ограничений и сравнение имён обнаруживает первый случай:

```text
AssertionError: CHECK constraints are out of sync with ORM models:
  Check constraint 'chk_orders_amount_positive' on table 'orders' is in the models but not in the database.
```

Имена должны следовать `naming_convention` metadata. Иначе явное `chk_orders_amount_positive` БД сравнивается с анонимным `CheckConstraint("amount > 0")` модели и каждый запуск падает. Это практическая причина соглашения об именах: оно делает стороны сопоставимыми.

Значения enum нужно читать из `pg_enum`:

```text
AssertionError: Enum values are out of sync with ORM models:
  Enum type 'order_status' has values ['new', 'paid'] in the database and ['new', 'paid', 'shipped'] in the models.
```

Отсутствующий элемент enum проявляется быстро: приложение стартует и работает до первой записи нового значения. Тогда приходит `invalid input value for enum order_status: "shipped"`, обычно в новой функции уже после развёртывания.

## Что запускать в CI {#what-to-run-in-ci}

Проверки основных свойств и две для слепых зон autogenerate:

1. **Обновление пустой БД до head.** Миграции вообще выполняются.
2. **Каждая ревизия вперёд, назад, вперёд.** Откат работает, повторное применение возможно.
3. **Полный откат до base.** История обратима.
4. **Ровно одна вершина.** Ветки истории не остались необъединёнными.
5. **Схема соответствует моделям.** Autogenerate не даёт diff.
6. **CHECK-ограничения присутствуют под ожидаемыми именами** согласно соглашению.
7. **Значения enum совпадают** с `pg_enum`.

Шестая и седьмая проверки закрывают слепые зоны пятой. CHECK и enum — обычные объекты PostgreSQL, а не экзотика.

Нужна настоящая БД. SQLite не ответит, как PostgreSQL применил DDL. Контейнер на тестовую сессию, новая схема на тест; вся матрица запускается за несколько минут.

## Инструменты {#the-pieces}

Набор предоставляет базовый класс [alembic-gauntlet](https://bedrock-python.github.io/alembic-gauntlet/). Передайте `MetaData`, включите `migration_diff_compare_server_default = True` для defaults. Fixture контейнера и изолированной схемы входят в библиотеку. От вас нужен `env.py`, использующий переданные соединение и схему, как описано в [статье о тестах миграций](2026-09-07-five-alembic-migration-tests.md).

Расхождения второй половины стали причиной версии 0.3.0: прежний набор пропускал отсутствующее CHECK и значение enum.
