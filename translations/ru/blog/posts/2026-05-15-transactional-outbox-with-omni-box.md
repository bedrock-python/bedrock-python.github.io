---
date: 2026-05-15
authors:
  - alex
categories:
  - Libraries
  - Design
tags:
  - omni-box
  - kafka
  - sqlalchemy
  - patterns
---

# Паттерн Transactional Outbox на Python: omni-box

<div class="bdr-post__hero" data-bdr-post="2026-05-15-transactional-outbox-with-omni-box" role="img" aria-label="Одна транзакция сохраняет строку и событие, а отдельный процесс передаёт событие дальше" markdown="0"></div>

У распределённых систем есть классическая проблема: нужно обновить базу данных и опубликовать событие в Kafka в рамках одной операции, но общей транзакции между ними нет. Если сервис упадёт между `INSERT` и `kafka.produce()`, данные могут потеряться незаметно. **omni-box** решает эту задачу с помощью паттерна Transactional Outbox.

<!-- more -->

## Проблема двойной записи { #the-dual-write-problem }

Представьте `CreateUserUseCase`, которому нужно:

1. Добавить строку в таблицу `users` в Postgres.
2. Опубликовать событие `UserCreated` в Kafka для других сервисов.

В наивной реализации между двумя записями остаётся опасный промежуток:

```python
# ❌ Not atomic — crash between these two leaves data inconsistent
await session.execute(insert(UserDB).values(...))
await session.commit()
await kafka_producer.send("user-created", payload)  # might never run
```

Если процесс перезапустится после коммита, но до отправки в Kafka, другие сервисы так и не узнают о новом пользователе. Компенсировать такие ситуации на уровне приложения сложно, и при этом легко допустить ошибку.

## Паттерн Outbox { #the-outbox-pattern }

Решение — записать событие в *той же транзакции базы данных*, что и бизнес-данные. Затем фоновый процесс читает недоставленные события и публикует их в Kafka, отмечая каждое как доставленное после успешной отправки.

```text
┌─────────────────────────────────────────────┐
│  Одна транзакция Postgres                    │
│                                             │
│  INSERT INTO users ...                      │
│  INSERT INTO outbox_events (UserCreated)     │
│                                             │
└─────────────────┬───────────────────────────┘
                  │ COMMIT (атомарно)
                  ▼
         ┌────────────────┐
         │  Outbox Worker │  (читает outbox_events)
         └───────┬────────┘
                 │ kafka.produce()
                 ▼
         ┌────────────────┐
         │  Топик Kafka   │
         └────────────────┘
```

Бизнес-данные и событие либо вместе сохраняются в Postgres, либо вместе откатываются. После коммита воркер повторяет отправку, пока Kafka не подтвердит получение сообщения. Доставка имеет семантику at-least-once: одно событие может прийти повторно.

## Использование omni-box { #using-omni-box }

omni-box предоставляет таблицу `outbox_events`, фоновый процесс и интеграцию с Unit of Work. Внутри сценария использования:

```python
async with self._uow.transaction() as tx:
    user = await tx.users.create(email=email, name=name)

    # Written in the same transaction — zero chance of loss
    await tx.outbox.create(
        UserCreatedEvent(user_id=user.id, email=email)
    )
```

Outbox-воркер запускается как отдельная asyncio-задача и опрашивает таблицу недоставленных событий:

```python
from omni_box import OutboxWorker

worker = OutboxWorker(session_factory=session_factory, producer=kafka_producer)
await worker.run()
```

## Сторона Inbox { #the-inbox-side }

omni-box также реализует паттерн Inbox для идемпотентного потребления сообщений Kafka. Каждое входящее сообщение записывается в таблицу `inbox_events` перед обработкой. Если consumer упадёт и прочитает сообщение снова, проверка Inbox предотвратит повторную обработку:

```python
async with self._uow.transaction() as tx:
    if await tx.inbox.already_processed(message_id):
        return  # idempotent — skip

    await tx.inbox.record(message_id)
    await self._handle(message)
```

## Зачем библиотека? { #why-a-library }

Сам паттерн хорошо известен, но детали реализации имеют значение: интервал опроса, размер пакета, задержка между повторами при ошибках Kafka, схема таблицы, поддержка миграций. omni-box предоставляет всё это с разумными настройками по умолчанию и напрямую интегрируется с транзакционной моделью `unit-of-work-kit`, используемой в сервисах Bedrock.

Полная документация: [bedrock-python.github.io/omni-box](https://bedrock-python.github.io/omni-box/).
