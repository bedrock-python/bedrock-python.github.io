---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - sqlalchemy-foundation-kit
  - sqlalchemy
  - pgbouncer
  - postgresql
  - asyncpg
  - connection-pooling
---

# PgBouncer в режиме транзакций и async SQLAlchemy: рабочая конфигурация, которой не хватает в документации {#pgbouncer-transaction-mode-and-async-sqlalchemy-the-production-setup-nobody-documents-enough}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy" role="img" aria-label="При каждой транзакции соединение назначается заново, а состояние сессии больше не принадлежит клиенту" markdown="0"></div>

Конфигурация SQLAlchemy прекрасно работает напрямую с PostgreSQL. Затем перед БД ставят PgBouncer в режиме транзакций, ради которого обычно и нужен пулер, и прежние предположения перестают быть верными. Настройки сессии перетекают между запросами. Подготовленные запросы исчезают или конфликтуют. Схема, заданная при подключении, молча не применяется. Модульные тесты этого не видят: они обращаются к PostgreSQL напрямую. Измерим, что забирает transaction pooling, какие привычные исправления ещё нужны современному PgBouncer, какая настройка действительно ломает соединение и какую конфигурацию стоит собрать.

<!-- more -->

Все измерения выполнены с PostgreSQL 17 и PgBouncer 1.25.2 в контейнерах через [скрипты статьи](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-pgbouncer-async-sqlalchemy). Версии: SQLAlchemy 2.0.52, asyncpg 0.31.0, sqlalchemy-foundation-kit 0.3.0, Python 3.13.

## Что забирает режим транзакций {#what-transaction-mode-takes-away}

В режиме session PgBouncer закрепляет серверное соединение за клиентским на весь срок его жизни, почти не помогая большому числу одновременно подключённых клиентов. В режиме transaction оно назначается лишь на одну транзакцию и возвращается в пул на `COMMIT`. Тысяча соединений приложения может делить двадцать серверных. Цена — всё состояние PostgreSQL на уровне *сессии*, потому что сессия больше не ваша:

- `SET` вне транзакции меняет серверное соединение; следующий клиент наследует настройку.
- Именованные подготовленные запросы живут в серверном соединении; следующая транзакция клиента может попасть в другое.
- Advisory lock уровня сессии, `LISTEN`, временные таблицы и курсоры между транзакциями принадлежат соединению, которое может больше не достаться клиенту.
- Стартовые параметры подключения PgBouncer передаёт только в пределах поддерживаемого им отслеживания.

Первый пункт легко показать новичку. Один клиент выполняет обычный `SET` вне транзакции и возвращает серверное соединение в пул размером один. Второй спрашивает:

```text
client A ran SET search_path TO leaked; client B sees search_path = 'leaked'
```

Клиент B ничего не настраивал, но теперь читает и пишет в незнакомой схеме. Ошибка воспроизводится только у запросов, попавших в это соединение. `SET LOCAL` внутри транзакции заканчивается вместе с ней и безопасен; обычный `SET` через transaction pooler создаёт непредсказуемую область воздействия.

## Ошибка prepared statement и когда она исчезла {#the-prepared-statement-error-and-when-it-stopped-happening}

Знакомая по обсуждениям asyncpg с PgBouncer ошибка выглядит так:

```text
asyncpg.exceptions.InvalidSQLStatementNameError: prepared statement "__asyncpg_stmt_333__" does not exist
```

Asyncpg готовит запросы по имени и кеширует имена на соединение. Через transaction pooler следующая транзакция может попасть в серверное соединение, не видевшее этого имени. Привычные исправления — отключить кеш драйвера и давать уникальные имена, чтобы клиенты не конфликтовали. Вот двадцать клиентов, каждый дважды выполняет двадцать разных запросов со стандартными настройками драйвера:

```text
plain SQLAlchemy + asyncpg, driver defaults (statement cache on)
  direct to PostgreSQL                                                   ok=800  errors=none
  PgBouncer transaction mode, defaults (max_prepared_statements=200)     ok=800  errors=none
  PgBouncer transaction mode, max_prepared_statements=0 (pre-1.22)       ok=484  errors={'DBAPIError': 316}
      first error: prepared statement "__asyncpg_stmt_333__" does not exist
```

Перечитайте среднюю строку. На современном PgBouncer без специальных клиентских настроек классическая ошибка не возникает. Поддержка отслеживания подготовленных запросов протокола появилась в 1.21, затем стала включаться по умолчанию в последующих версиях: пулер знает, где какой запрос подготовлен, и при необходимости готовит его заново. Третья строка — та же нагрузка с принудительно отключённой поддержкой, то есть условия старых руководств: около сорока процентов ошибок.

Итак, привычные советы верны лишь для части конфигураций. Если PgBouncer старый или `max_prepared_statements = 0`, нужно отдельно учитывать кеширование и уникальность имён. В актуальной конфигурации дополнительные настройки дают небольшой запас совместимости ценой обмена по сети. Но важнейшая настройка была другой.

## Настройка, которая действительно ломает подключение {#the-setting-that-actually-breaks-the-connection}

Она выглядит безобидно: стартовый параметр. Asyncpg позволяет передать `server_settings` при подключении. Естественно указать `jit=off`, поскольку JIT способен давать задержки на коротких запросах, или `search_path=app`, если таблицы в отдельной схеме. Оба приходят в PgBouncer как параметры старта. Незнакомый отслеживанию параметр он не просто пропускает: он отклоняет соединение:

```text
sqlalchemy-foundation-kit 0.2.1, its "pgbouncer-safe" settings
  PgBouncer transaction mode, defaults     ok=0    errors={'ProtocolViolationError': 800}
      first error: unsupported startup parameter: jit
```

Ноль подключений. Так работала предыдущая версия моей библиотеки с настройками, которые её же документация требовала для PgBouncer. Я обнаружил это, построив таблицу измерений. Администраторский обход `ignore_startup_parameters = jit,search_path` разрешает подключение и делает ровно то, что обещает:

```text
                                                        jit    search_path
  direct to PostgreSQL                                  off    app
  PgBouncer, ignore_startup_parameters=jit,search_path  on     "$user", public
```

Параметры игнорируются. JIT включён, схема стандартная, запросы идут в `public`. Библиотека приняла настройку, драйвер отправил, БД не применила — и нигде нет ошибки. Худшая конфигурация: работает в окружении без пулера.

Вывод: настройки сессии нельзя бездумно задавать клиентом через transaction pooler. Их нужно установить там, где создаётся сессия, например `ALTER ROLE app SET search_path = app` и `ALTER ROLE app SET jit = off`; либо настроить поддерживаемое отслеживание PgBouncer; либо применять первым запросом каждой транзакции через `SET LOCAL`. Последний вариант контролирует приложение. Так делает исправленная библиотека:

```text
sqlalchemy-foundation-kit 0.3.0
  PgBouncer transaction mode, defaults     ok=800  errors=none
  jit_probe through PgBouncer              jit='on'  search_path='app'
```

`jit` больше не отправляется без явного запроса. `db_schema` применяется через `set_config('search_path', ..., true)` по событию engine в начале каждой транзакции: внутри уже закреплённого PgBouncer соединения и только до её конца. Проверка показывает нужную схему через пулер и JIT согласно серверной настройке.

## Размеры пулов, когда перед пулом есть ещё пул {#pool-sizing-when-there-is-a-pool-in-front-of-your-pool}

Два пула, два набора ограничений, которые нужно согласовать:

```text
application     pool_size + max_overflow, per process     x  processes  =  client connections PgBouncer must accept
PgBouncer       max_client_conn                                          >= that number
PgBouncer       default_pool_size, per user/database pair                =  server connections PostgreSQL actually sees
PostgreSQL      max_connections                                          >  sum of every PgBouncer's pools, plus admins
```

Пул приложения ограничивает одновременные транзакции одного процесса. Десять соединений плюс двадцать overflow — частое, обычно слишком щедрое значение для async-сервиса: сотни запросов процесса большую часть времени ждут не БД. Пул PgBouncer ограничивает серверные соединения пользователя, за которые PostgreSQL платит памятью и конкуренцией блокировок. Польза в большом первом числе и небольшом втором. Она исчезает, если `default_pool_size` просто приравнять к сумме пулов приложений.

В эксперименте серверный пул из пяти соединений обслужил двадцать клиентов и восемьсот запросов без заметного ожидания.

## Что наблюдать {#what-to-monitor}

Предвестник проблем — время ожидания соединения, а не только число занятых. Полностью занятый пул без очереди может быть настроен правильно; растущее ожидание требует смотреть время операций и распределение нагрузки. Библиотека предоставляет состояния пула, ожидание перед ним и время удержания полученного соединения, от которого очередь зависит:

```text
postgres_db_pool_size                             gauge      what the pool is configured for
postgres_db_pool_checked_out                      gauge      connections in use right now
postgres_db_pool_overflow                         gauge      connections beyond pool_size, in use
postgres_db_connection_checkout_wait_seconds      histogram  how long a caller waited for a connection
postgres_db_connection_held_duration_seconds      histogram  how long it held the connection afterwards
postgres_db_connection_timeouts_total             counter    callers that never got one
```

Настраивайте тревоги по ожиданию и таймаутам, остальное выводите на графики. В [статье о мониторинге пула](2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool.md) измерены все шесть показателей при исчерпании пула. У PgBouncer `SHOW POOLS` даёт `cl_waiting` и `maxwait`: число клиентов в очереди к серверному соединению и возраст самого старого ожидания. Рост `maxwait` при ровном ожидании приложения указывает на очередь ниже; если растут оба, нужно исследовать и ёмкость PgBouncer, и длительность работы PostgreSQL.

## Закрытие пулов при обновлении {#closing-pools-during-a-rollout}

Последняя ловушка — завершение. У заменяемого pod ещё могут выполняться транзакции; преждевременное закрытие используемых ресурсов способно сорвать запросы и оборвать соединения посреди транзакций. Порядок: прекратить приём новой работы, дождаться текущих транзакций, затем вызвать dispose engine с ограничением времени, чтобы зависшее освобождение не пережило бюджет pod. Менеджер session библиотеки ограничивает dispose таймаутом и не выпускает из него исключения; безопасный порядок описан в [статье об остановке](2026-09-07-graceful-shutdown-is-a-protocol.md).

## Конфигурация {#the-configuration}

Всё выше в виде реально создаваемого engine:

```python
from pydantic import SecretStr
from sqlalchemy_foundation_kit import create_async_session_manager
from sqlalchemy_foundation_kit.contrib.settings import BasePostgresConfig, ConnectionSettings, PoolSettings

config = BasePostgresConfig(
    connection=ConnectionSettings(host="pgbouncer", port=6432, user="app", password=SecretStr("..."), database="app"),
    pool=PoolSettings(size=5, max_overflow=5),    # per process; PgBouncer's default_pool_size is the real limit
    application_name="orders",                    # the one startup parameter PgBouncer tracks and you want
    db_schema="app",                              # applied per transaction, not at connect
)
manager = create_async_session_manager(config)   # statement caches off, unique statement names, no jit, no search_path at startup
```

Измерения оставили три решения: нулевые кеши и уникальные имена как совместимость со старыми конфигурациями PgBouncer; схема внутри транзакции; имя приложения, которое стоит передавать при подключении, поскольку PgBouncer поддерживает его, а `pg_stat_activity` показывает. Не выдержал проверки `jit` как стартовый параметр. Хорошо, что об этом сообщила таблица эксперимента, а не развёртывание.

Это конфигурация [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/guide/configuration/#pgbouncer). Версия 0.3.0 перестала отправлять два параметра, которые PgBouncer отклонял. Библиотека существовала до статьи; раздел её руководства о PgBouncer появился благодаря ей.
