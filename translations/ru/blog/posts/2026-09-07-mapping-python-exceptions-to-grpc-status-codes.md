---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - grpc-server-kit
  - grpc
  - errors
  - security
  - api-design
---

# Как отображать исключения Python в статусы gRPC без утечки внутренних данных {#mapping-python-exceptions-to-grpc-status-codes-without-leaking-internals}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-mapping-python-exceptions-to-grpc-status-codes" role="img" aria-label="Много типов исключений превращаются в несколько статусов, а внутренние данные остаются на сервере" markdown="0"></div>

У gRPC шестнадцать кодов ошибок помимо успешного статуса, а у вашего сервиса сотня типов исключений: кому-то нужно задать соответствие. Плохая реализация создаёт две проблемы: клиент не отличает временную ошибку от постоянной, а текст исключения уходит по сети любому вызывающему. Я пропустил одиннадцать исключений через четыре конфигурации сервера и прочитал ответы клиента. В двух оказался пароль БД.

<!-- more -->

Результаты получены в [эксперименте статьи](../lab/2026-09-07-python-exceptions-to-grpc-status-codes/README.md). Версии: grpc-server-kit 0.1.1, grpcio 1.83.1, Python 3.13.

## Если отображения вообще нет {#what-happens-with-no-map-at-all}

```text
    ValueError        UNKNOWN  "Unexpected <class 'ValueError'>: amount must be positive"
    PermissionError   UNKNOWN  "Unexpected <class 'PermissionError'>: token lacks scope orders:write"
    ConnectionError   UNKNOWN  "Unexpected <class 'ConnectionError'>: could not connect to
                               postgresql://orders:hunter2@db.internal:5432/orders"
    RuntimeError      UNKNOWN  "Unexpected <class 'RuntimeError'>: ledger write failed against
                               postgresql://orders:hunter2@db.internal:5432/orders"
```

Все ошибки становятся `UNKNOWN`, все сообщения исключений — публичными.

`UNKNOWN` создаёт эксплуатационную проблему: клиент не отличает неверный запрос от недоступной БД, и политике повторов не на что опереться. Повторять всё — превратить плохой запрос в лавину; не повторять ничего — показать пользователю временный сбой.

Сообщение создаёт проблему безопасности, вполне реальную. Два исключения содержат строку подключения, потому что драйвер включает её в ошибку. Никто не планировал публиковать её. Стандартное поведение gRPC передаёт представление исключения в деталях статуса: удобно для отладки, не подходит серверу.

## Стандартное отображение {#the-default-map}

```text
    ValueError           INVALID_ARGUMENT     'Invalid request data'
    PermissionError      PERMISSION_DENIED    'Permission denied'
    FileNotFoundError    NOT_FOUND            'Resource not found'
    TimeoutError         DEADLINE_EXCEEDED    'Deadline exceeded'
    NotImplementedError  UNIMPLEMENTED        'Method is not implemented'
    KeyError             INTERNAL             'Internal server error'
    ConnectionError      INTERNAL             'Internal server error'
    RuntimeError         INTERNAL             'Internal server error'
```

Пять стандартных исключений получают соответствующие смыслу статусы. Всё остальное становится `INTERNAL`; сообщения заменяются безопасными строками по статусу. Пароли исчезают.

Важен стандарт `INTERNAL`: **неизвестное отображению исключение считается ошибкой сервиса и превращается в `INTERNAL` без подробностей.** Клиент узнаёт, что проблема не в нём и идентичный повтор, вероятно, не поможет. Настоящее сообщение остаётся в журнале вместе с traceback.

## Отображение — контракт клиента, а не форматирование {#the-map-is-a-client-contract-not-a-formatting-decision}

Полезным отображение становится после добавления ошибок вашего сервиса:

```text
    OrderNotFound     NOT_FOUND            'Resource not found'
    OrderAlreadyPaid  FAILED_PRECONDITION  'Failed precondition'
    RateLimited       RESOURCE_EXHAUSTED   'Resource exhausted'
    ConnectionError   UNAVAILABLE          'Service unavailable'
```

Каждая строка говорит, что делать клиенту; код — машиночитаемая часть этого решения:

| Статус | Действие клиента |
|---|---|
| `INVALID_ARGUMENT` | Исправить запрос; не повторять неизменённым |
| `NOT_FOUND` | Объекта нет; повтор его не создаст |
| `FAILED_PRECONDITION` | Состояние не подходит; повторять только после его изменения |
| `PERMISSION_DENIED` / `UNAUTHENTICATED` | Исправить права или учётные данные; не повторять с теми же |
| `RESOURCE_EXHAUSTED` | При ограничении частоты выдержать паузу, затем повторить |
| `UNAVAILABLE` | Повторить с задержкой; другая реплика может ответить |
| `DEADLINE_EXCEEDED` | Время вызова истекло; работа могла выполниться или нет |
| `ABORTED` | Конфликт конкурентных операций; повторить на более высоком уровне |
| `INTERNAL` | Ошибка сервера; идентичный повтор вряд ли поможет |

Два пункта требуют особого внимания.

**`ConnectionError` как `UNAVAILABLE` имеет последствия.** Этот статус велит клиентам повторять. Это полезно при кратком сбое БД и опасно после часа недоступности, когда повторы мешают восстановлению. Код правильный, но именно поэтому клиенту нужны бюджет и circuit breaker, а не только число попыток.

**`DEADLINE_EXCEEDED` не говорит, выполнена ли работа.** Запись с таймаутом могла зафиксироваться. Поэтому здесь особенно нужен ключ идемпотентности на другой стороне; повтор по этому статусу безопасен только для повторяемых операций.

Не используйте `ALREADY_EXISTS` там, где нет дубликата. Он кажется подходящим для «этот заказ уже оплачен», но клиентская библиотека может считать его успехом — «ваша операция создания уже прошла» — и молча проглотить ситуацию.

## Подробности: два уровня доверия {#details-the-two-tier-rule}

Безопасные сообщения по статусу честны, но малоинформативны: `Failed precondition` не объясняет, *какое* условие нарушено. Нужно разделить исключения на две группы:

```text
    ValueError        INVALID_ARGUMENT     'Request processing failed'
    ConnectionError   UNAVAILABLE          'Request processing failed'
    RuntimeError      INTERNAL             'Request processing failed'
    OrderNotFound     NOT_FOUND            'OrderNotFound: order 42'
    OrderAlreadyPaid  FAILED_PRECONDITION  'OrderAlreadyPaid: order 42 was paid at 09:12'
    RateLimited       RESOURCE_EXHAUSTED   'RateLimited: 100 requests per minute'
```

Ошибки предметной области, определённые сервисом, могут передавать сообщение: вы специально написали его для клиента и оставили только допустимые факты. Всё остальное, включая стандартные исключения из вашего кода, получает общую строку. Их сообщения пишут библиотеки, драйверы и стандартная библиотека, авторы которых не думают об аудитории вашего API.

Полезное правило: **публиковать сообщение можно только у явно разрешённого типа ошибки вашего сервиса, чей текст предназначен клиенту.** Оно проверяется при ревью и сохраняет безопасное поведение, когда кто-то добавил новый тип и не подумал о публикации.

Для данных сложнее предложения используйте `error_details` gRPC вместо структуры внутри строки details. Машиночитаемые сведения в trailing metadata позволяют клиенту выбирать поведение, а человеческий текст остаётся текстом.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Разделите выбор статуса и публичного сообщения</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="1" data-search-exclude>

```mermaid
---
config:
  theme: default
  look: classic
  flowchart:
    useMaxWidth: false
    wrappingWidth: 150
    padding: 12
    nodeSpacing: 24
    rankSpacing: 32
---
flowchart TD
    accTitle: Разделите выбор статуса и публичного сообщения
    accDescr: Для доменной ошибки можно вернуть заранее выбранное объяснение клиенту. Неожиданному внутреннему исключению нужны общий ответ и подробная запись на сервере.
 E["Исключение Python"] --> M["Выбрать статус gRPC"]
 E --> P{"Известная публичная доменная ошибка?"}
 P -->|"Да"| D["Безопасное доменное сообщение"]
 P -->|"Нет"| G["Общее сообщение"]
 E -.-> L["Серверные журналы и трассировка"]
 M --> R["Ответ gRPC"]
 D --> R
 G --> R
```

</div>
<p class="bdr-diagram__caption">Для доменной ошибки можно вернуть заранее выбранное объяснение клиенту. Неожиданному внутреннему исключению нужны общий ответ и подробная запись на сервере.</p>
</figure>
<!-- /diagram:concept -->

## Где чему место {#what-belongs-where}

- **Отображение живёт в транспортном слое**, не в обработчиках. Обработчик, ловящий своё исключение ради статуса, переносит проектирование API в бизнес-логику; следующий выберет иначе.
- **Предметная область не импортирует `grpc`.** Она выбрасывает `OrderNotFound`, который нужен и HTTP-точке входа того же сценария. О двух транспортах — [отдельная статья](2026-09-07-transport-independent-errors.md).
- **Намеренные прерывания проходят без изменений.** `context.abort` уже выбрал статус; слой отображения не должен его переписывать, а сборщик ошибок — считать багом. Это [ловушка порядка перехватчиков](2026-09-07-the-anatomy-of-a-production-grpc-server.md).
- **Журнал получает всё необходимое для диагностики:** тип, сообщение, traceback, correlation id. Общий текст по сети имеет смысл, только если подробности доступны в защищённом журнале.

## Инструменты {#the-pieces}

Отображение, безопасные сообщения и фабрика подробностей есть в [grpc-server-kit](https://bedrock-python.github.io/grpc-server-kit/). Перехватчик объединяет вашу карту со стандартной, по умолчанию заменяет details безопасной строкой, журналирует настоящее исключение с traceback и не трогает намеренные прерывания. Пять встроенных типов — отправная точка; главная часть карты — ошибки вашей предметной области.

Одиннадцать исключений, два пароля, одна карта соответствий.
