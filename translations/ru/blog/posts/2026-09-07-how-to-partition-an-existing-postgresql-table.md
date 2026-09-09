---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - pg-partsmith
  - postgresql
  - partitioning
  - migrations
  - zero-downtime
---

# Как партиционировать существующую таблицу PostgreSQL без переписывания приложения {#how-to-partition-an-existing-postgresql-table-without-rewriting-your-application}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-how-to-partition-an-existing-postgresql-table" role="img" aria-label="Превратить старую таблицу в DEFAULT-партицию и переносить данные по окнам, продолжая запись" markdown="0"></div>

`ALTER TABLE ... PARTITION BY` не существует. Чтобы сделать рабочую таблицу партиционированной, нужно создать нового родителя, присоединить старую таблицу как DEFAULT-партицию и освобождать её по окнам, пока приложение продолжает писать. Я сделал это с двумя миллионами строк, непрерывно работающим writer и reader, считающим старейший месяц. Измерил каждый шаг: блокировки, их длительность и видимое приложению состояние. Запрос записи не изменился, ни одна строка не оказалась одновременно в двух местах.

<!-- more -->

Числа получены в [эксперименте статьи](../lab/2026-09-07-partition-existing-table/README.md) с PostgreSQL 17 в контейнере. Writer вставляет строку каждые 5 мс, reader считает старейший месяц каждые 20 мс. Версии: pg-partsmith 1.5.1, asyncpg 0.31.0, Python 3.13.

Таблица `events`: два миллиона строк за год, 263 МБ с индексами, `PRIMARY KEY (id)`. Есть таблица `event_notes` с внешним ключом на неё.

## Шаг 1: первичный ключ должен включать колонку партиционирования {#step-1-the-primary-key-has-to-contain-the-partition-column}

Первое препятствие — ключ, а не данные:

```text
    CREATE TABLE ... (LIKE events INCLUDING ALL) PARTITION BY RANGE (created_at):
      FeatureNotSupportedError: unique constraint on partitioned table must include all
      partitioning columns
```

Поэтому сначала `PRIMARY KEY (id)` нужно заменить на `PRIMARY KEY (id, created_at)`. Второе препятствие: на старом ключе уже держатся другие объекты:

```text
    ALTER TABLE events DROP CONSTRAINT events_pkey:
      DependentObjectsStillExistError: cannot drop constraint events_pkey on table events
      because other objects depend on it
```

Внешний ключ `event_notes` зависит от этого индекса. Его нужно сначала убрать, а вернуть в конце уже в другой форме. Это настоящая цена партиционирования по времени и [аргумент в пользу упорядоченного по времени идентификатора](2026-09-07-uuidv7-as-a-postgresql-partition-key.md), если вы проектируете схему сейчас, а не мигрируете существующую.

Сам ключ можно изменить двумя способами; разницу ощущают записывающие процессы:

```text
    DROP CONSTRAINT, ADD PRIMARY KEY (id, created_at):        422 ms
      writer: p50 412.7 ms, longest 413 ms
    CREATE UNIQUE INDEX CONCURRENTLY events_id_created_at_key: 477 ms
    DROP CONSTRAINT, ADD PRIMARY KEY USING INDEX:               3 ms
      writer: p50 1.3 ms, longest 37 ms
```

`ADD PRIMARY KEY` строит индекс под `ACCESS EXCLUSIVE`, поэтому запись ждёт всё построение: здесь 413 мс, на ста миллионах строк — минуты. Если сначала построить индекс `CONCURRENTLY`, а затем назначить его первичным ключом, блокировка длится три миллисекунды. Результат одинаков, разница — между короткой задержкой и недоступностью.

У конкурентного пути две особенности: его нельзя выполнять внутри транзакции, а при сбое может остаться невалидный индекс, который нужно удалить перед повтором. С обоими можно работать, если знать заранее.

## Шаг 2: подмена таблицы {#step-2-the-swap}

Одна транзакция, четыре запроса, две миллисекунды:

```sql
BEGIN;
SET LOCAL lock_timeout = '2s';
ALTER TABLE events RENAME TO events_legacy;
ALTER INDEX events_created_at_idx RENAME TO events_legacy_created_at_idx;
ALTER TABLE events_legacy RENAME CONSTRAINT events_pkey TO events_legacy_pkey;
CREATE TABLE events (LIKE events_legacy INCLUDING ALL) PARTITION BY RANGE (created_at);
ALTER TABLE events ATTACH PARTITION events_legacy DEFAULT;
COMMIT;
```

```text
    one transaction: 2 ms
    live rows written so far: 62, in the DEFAULT partition: 51
```

Сразу после фиксации все строки снова видны через `events`, а `INSERT INTO events ...` приложения продолжает работать, не замечая перемен. Записи во время подмены попали в DEFAULT-партицию — старую таблицу, куда попали бы и раньше.

`lock_timeout` здесь необходим. Транзакции на мгновение нужна `ACCESS EXCLUSIVE`; если её не даёт долгий запрос, лучше прервать подмену через две секунды, чем поставить её в очередь, за которой выстроятся все новые запросы. Задайте таймаут и при его срабатывании повторяйте транзакцию целиком.

## Шаг 3: первое обслуживание {#step-3-the-first-maintenance-tick}

Родитель существует, теперь нужны партиции. Первый запуск создаёт текущий месяц и следующие:

```text
    plan for public.events:
      CREATE public.events__2026_09 (create_ahead)
      CREATE public.events__2026_10 (create_ahead)
      CREATE public.events__2026_11 (create_ahead)
    created 3, issues 0, error None, 976 ms
    live rows: 109 in this month's partition, 0 left in DEFAULT
    writer: 53 inserts, longest 540 ms
```

Интересен текущий месяц: writer пишет в него прямо во время создания. PostgreSQL не присоединит партицию, пока соответствующие строки остаются в DEFAULT. Их нужно перенести, но любая вставка между переносом и присоединением снова помешает. Перенос и присоединение должны выполняться под одной блокировкой: так 109 живых строк оказываются в новой партиции без остатков.

Самая медленная вставка на этом шаге заняла 540 мс из-за ожидания блокировки. Это цена операции, зависящая от объёма текущего месяца, ещё лежащего в DEFAULT.

## Шаг 4: перенос данных {#step-4-the-drain}

Остальные двенадцать месяцев всё ещё в старой таблице. Переносим пакетами, начиная со старейшего окна:

```text
    5 calls, 47 batches, 1,964,376 rows moved into 12 partitions in 13.9 s
    writer: 1938 inserts, p50 0.8 ms, longest 93 ms
    reader: lowest count 28771 of 128771, below full in 6 of 418 samples
      the oldest month was below its full count for about 0.5 s
```

Два миллиона строк за четырнадцать секунд; медиана вставки writer всё время 0,8 мс. Каждый пакет — `DELETE ... RETURNING`, передающий строки в `INSERT`, с отдельной фиксацией. В каждой зафиксированной точке строка находится ровно в одном месте, а прерывание стоит одного пакета.

Строка reader показывает существенное ограничение. Пока окно переносится, строки находятся в ещё не присоединённой партиции и не видны через родителя: около полусекунды старейший месяц показывал 28 771 строку вместо 128 771. PostgreSQL не допускает другого порядка: нельзя присоединить партицию, пока DEFAULT хранит её строки. Поэтому приходится выбирать между кратким недосчётом по месяцу и окном обслуживания без читателей. Строки в уже присоединённых партициях и строки других окон в DEFAULT остаются видимыми.

Меньшие пакеты сокращают отдельные операции переноса, но удлиняют весь процесс; невидимость сохраняется до присоединения окна. Если читатели совсем не допускают временного недосчёта, выполняйте перенос в тихий час с ограничением соответствующих чтений либо учитывайте кратковременное занижение отчётов за переносимый месяц.

## Шаг 5: внешний ключ возвращается составным {#step-5-the-foreign-key-comes-back-composite}

```text
    ADD FOREIGN KEY (event_id) REFERENCES events (id):
      InvalidForeignKeyError: there is no unique constraint matching given keys for
      referenced table "events"
    ADD COLUMN event_created_at:                             1 ms
    backfill it from events (50,000 notes):               2003 ms
    ADD FOREIGN KEY (event_id, event_created_at) NOT VALID:   4 ms
    VALIDATE CONSTRAINT:                                   381 ms
```

Ссылающейся таблице тоже нужна колонка партиционирования: единственный уникальный ключ родителя — `(id, created_at)`. Поэтому в `event_notes` добавляется и заполняется колонка, а ограничение создаётся в два этапа. `NOT VALID` берёт короткую блокировку без сканирования, затем `VALIDATE CONSTRAINT` сканирует, не блокируя запись. Четыре и 381 миллисекунда вместо одного запроса с блокировкой на всё сканирование.

Делайте это *после* переноса. Строки, на которые уже ссылаются, переносить нельзя: механизм откажется, чтобы не повредить ссылки. Внешний ключ во время переноса превратит миграцию в последовательность отказов.

## Шаг 6: пустая DEFAULT-партиция и последовательность {#step-6-the-empty-default-and-the-sequence}

Старая таблица пуста, её можно удалить. Но:

```text
    DETACH PARTITION events_legacy: 157 ms
    DROP TABLE events_legacy:
      DependentObjectsStillExistError: cannot drop table events_legacy because other objects
      depend on it
      DETAIL: default value for column id of table events depends on sequence events_id_seq
              default value for column id of table events__2025_09 depends on ...
              (one line per partition)
    the sequence events_id_seq is owned by: events_legacy
    ALTER SEQUENCE events_id_seq OWNED BY events.id: 0 ms
    DROP TABLE events_legacy: 32 ms
```

Об этом шаге обычно забывают. `BIGSERIAL` создал последовательность, *принадлежащую* колонке исходной таблицы. `LIKE ... INCLUDING ALL` назначил новому родителю и каждой партиции значение по умолчанию `nextval('events_id_seq')`. Удаление старой таблицы потянуло бы последовательность за собой, поэтому PostgreSQL отказывается ломать пятнадцать таблиц. Подсказка `HINT` предлагает `CASCADE`, который здесь удалит значения по умолчанию со всех партиций и сломает вставки.

Исправление — один дешёвый запрос: передать владение последовательностью колонке нового родителя, затем удалить старую таблицу. Именно так, без `CASCADE`. Проверьте это на репетиции, а не в три часа ночи.

## Результат {#the-result}

```text
    events__2025_09  128390 rows   ...  events__2026_08  169671 rows
    events__2026_09   37362 rows   events__2026_10  0   events__2026_11  0
    2,001,930 rows through the parent; the writer inserted 1930, 1930 are there
    the writer's statement never changed:
      INSERT INTO events (created_at, kind, payload) VALUES (now(), 'live', $1)
```

Два миллиона исходных строк плюс все вставленные во время миграции находятся в двенадцати месячных партициях; ещё два месяца созданы заранее. Приложение не изменило ни одного запроса.

## Порядок действий и риски {#the-order-and-where-the-risk-is}

1. Построить `CREATE UNIQUE INDEX CONCURRENTLY` и назначить его первичным ключом — без долгого исключительного блокирования. Зависимые внешние ключи снять до замены старого ключа.
2. Убедиться, что входящие внешние ключи сняты.
3. Выполнить подмену одной транзакцией с `lock_timeout`.
4. Запустить первое обслуживание для текущего месяца.
5. Перенести остальные данные пакетами от старых окон к новым.
6. Вернуть составные внешние ключи через `NOT VALID`, затем `VALIDATE`.
7. Передать последовательность новому владельцу, отсоединить и удалить старую таблицу.

Два действительно рискованных шага — замена ключа и подмена таблицы. Обоим нужны короткие исключительные блокировки; `lock_timeout` превращает потенциальную недоступность в повтор операции. Всё далее выполняется постепенно и возобновляется: прерванный перенос оставляет частично заполненную отсоединённую партицию, следующий вызов завершает работу.

Отрепетируйте на копии с рабочим количеством строк. Числа зависят от размера таблицы, и заранее особенно важно узнать длительность `CREATE INDEX CONCURRENTLY` именно на ваших данных.

## Инструменты {#the-pieces}

Обслуживание, план и перенос предоставляет [pg-partsmith](https://bedrock-python.github.io/pg-partsmith/). `partition_data` перемещает строки DEFAULT-партиции в соответствующие окна ограниченными пакетами, создаёт партиции по мере продвижения и присоединяет их после освобождения окна под блокировкой, объединяющей последний пакет и присоединение. DDL подмены остаётся вашим: эти четыре запроса нужно прочитать перед запуском на собственной таблице.

Четырнадцать секунд переноса, две короткие исключительные блокировки и одна неожиданная последовательность.
