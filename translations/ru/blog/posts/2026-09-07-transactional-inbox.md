---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - omni-box
  - kafka
  - inbox
  - outbox
  - idempotency
  - postgresql
---

# Транзакционный inbox: вторая половина паттерна outbox {#transactional-inbox-the-other-half-of-the-outbox-pattern}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-transactional-inbox" role="img" aria-label="Входящее сообщение становится строкой в одной транзакции с его эффектом" markdown="0"></div>

Outbox заметнее, потому что решает драматичную проблему: событие не ушло. Inbox решает тихую: событие пришло дважды либо consumer погиб посреди обработки. С этим сталкивается каждый Kafka consumer. Часто решение — комментарий «обработчики должны быть идемпотентными», который соблюдает автор первого и забывает автор четвёртого. Здесь inbox рассмотрен как механизм: строка на сообщение в БД потребителя в одной транзакции с эффектом. Измерим, что разные стратегии подтверждения делают при сбое обработчика посередине.

<!-- more -->

Числа получены [скриптом статьи](../lab/2026-09-07-transactional-inbox/README.md) и сценарием inbox из [эксперимента exactly-once](../lab/2026-09-07-exactly-once-effects/README.md), оба с PostgreSQL 17 и Kafka в контейнерах. Версии: omni-box 0.2.0, aiokafka 0.14.0, Python 3.13.

## Две проблемы потребителя {#the-consumers-two-problems}

В рассматриваемой схеме брокер доставляет как минимум один раз, а [outbox](2026-09-07-exactly-once-effects.md) отправителя намеренно выбирает возможные дубликаты вместо потерь. Потребитель увидит повтор после перераспределения, сбоя между обработкой и фиксацией смещения или повторной публикации relay. Это первая проблема.

Вторая тоньше. Обработчик записал счёт, затем упал при сетевом вызове или из-за бага во второй половине функции. Если счёт уже отдельно зафиксирован, а сообщение не подтверждено, повтор создаст второй. При обратном порядке — сначала offset, потом фиксация записи — сбой оставит ни счёта, ни повторной доставки. Эффект расходится с подтверждением по той же причине, что у отправителя: две системы, две фиксации.

## Строка inbox {#the-inbox-row}

Inbox — таблица БД потребителя с уникальным индексом `(message_id, consumer_group)`. Для обработки открывается транзакция, вставляется строка inbox, *в той же транзакции* выполняется обработчик, затем commit. Его записи и строка фиксируются вместе либо не фиксируются. Повторная вставка конфликтует с ключом — значит, сообщение уже обработано и его можно пропустить.

```python
async def create_invoice(event: InboxEvent, repo: InboxEventRepository) -> None:
    await repo.session.execute(invoices.insert().values(order_id=event.payload["order_id"]))


runner = InboxConsumerRunner(
    consumer=KafkaEventConsumer(kafka_consumer),
    transaction_provider=InboxTxProvider(session_factory),   # opens the transaction, yields the repository
    handler=create_invoice,                                   # runs inside it, writes through repo.session
    worker_id="billing-1",
    consumer_group="billing",                                 # part of the key: each group gets its own once
)
```

Обработчик пишет через `repo.session`, ту самую транзакцию строки inbox. В этой строке вся гарантия. Собственная session обработчика вернула бы две независимые фиксации.

Измеренный случай дубликата из эксперимента exactly-once: relay поместил одно сообщение в топик дважды:

```text
delivery 1: processed=True  duplicate=False  committed=True   invoices=1
delivery 2: processed=False duplicate=True   committed=True   invoices=1
```

Вторая доставка нашла строку, сообщила о дубликате, зафиксировала offset и не запускала обработчик.

## Измерение: ошибка посреди обработки {#measured-the-handler-fails-halfway}

При падающем обработчике стратегия подтверждения определяет потерю, дубликат или однократный результат. Скрипт отправляет сообщение, запускает обработчик, записывающий счёт и выбрасывающий исключение, останавливает consumer и запускает нового в той же группе. Четыре стратегии:

```text
AT_MOST_ONCE                       first: processed=False committed=True   second consumer: nothing delivered   handler ran=1  invoices=0
AT_LEAST_ONCE, commit ON_PERSIST   first: processed=False committed=True   second consumer: nothing delivered   handler ran=1  invoices=0
AT_LEAST_ONCE, commit ON_SUCCESS   first: processed=False committed=False  second consumer: processed=True      handler ran=2  invoices=1
EXACTLY_ONCE_INBOX (default)       first: processed=False committed=False  second consumer: processed=True      handler ran=2  invoices=1
```

Первые две теряют работу. `AT_MOST_ONCE` фиксирует offset до действий — допустимо для телеметрии, которую дешевле потерять, чем повторить, но не для счёта. `AT_LEAST_ONCE` с фиксацией при persist подтверждает после транзакции *независимо от её исхода*. Транзакция откатилась, сообщение подтверждено, эффекта нет. Название описывает доставку, но не гарантирует результат обработки; режим предназначен случаям, где сбой записывается и повторяется отдельно.

Последние две дают один счёт. Обработчик запускался дважды: первая ошибка откатила и счёт, и inbox, оставив offset незафиксированным. Новый consumer получил сообщение, вторая обработка записала единственный счёт. Это однократный *эффект*, а не однократный запуск обработчика. Стандарт `EXACTLY_ONCE_INBOX` — последняя строка; от предыдущей отличается обработкой дубликатов и занятых записей, которую runner берёт на себя.

## Чего inbox не делает {#what-the-inbox-does-not-do}

Не делает однократным эффект *вне* БД. Отправленное перед ошибкой письмо уйдёт снова при повторе: оно не входит в транзакцию. Защищены только эффекты той же БД; остальным нужен собственный ключ, как в [статье об идемпотентности](2026-09-07-idempotency-keys-the-part-everyone-gets-wrong.md) для исходящего вызова.

Не дедуплицирует вечно. Окно равно сроку жизни строки; очистка делает старое сообщение новым. Срок должен превышать период возможной повторной доставки брокера.

И не выполняет собственные повторы. Runner не хранит отдельную запись сбоя или счётчик попыток; повтор приходит от брокера. Для повтора из inbox понадобилась бы строка, а она откатилась вместе с ошибкой.

## Две половины {#the-pair}

Outbox и inbox — один паттерн с двух сторон. Отправитель записывает событие рядом со своим состоянием и доставляет relay как минимум один раз. Получатель записывает отметку рядом с эффектом и устраняет повтор уникальным ключом. Ни одной стороне не нужна идеальная доставка другой. Вместе они обеспечивают однократные транзакционные эффекты — именно ради них обычно и спорят о числе сообщений.

Runner, репозиторий и строка — сторона inbox в [omni-box](https://bedrock-python.github.io/omni-box/). Она разделяет pipeline и PostgreSQL-репозиторий с outbox, работая в переданной транзакции.

Суть — в третьем столбце: `invoices=0`, `invoices=0`, `invoices=1`, `invoices=1`.
