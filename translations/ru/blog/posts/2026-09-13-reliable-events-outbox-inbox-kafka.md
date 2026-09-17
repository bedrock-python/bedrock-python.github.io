---
date: 2026-09-13
authors:
  - alex
categories:
  - Design
tags:
  - omni-box
  - kafka
  - outbox
  - inbox
  - postgresql
---

# Надёжная доставка событий: Outbox, Inbox и сбои Kafka {#reliable-events-outbox-inbox-kafka}

<div class="bdr-post__hero" data-bdr-post="2026-09-13-reliable-events-outbox-inbox-kafka" role="img" aria-label="Две системы, две фиксации, нет общей транзакции: закрываем каждое окно сбоя по очереди" markdown="0"></div>

Сервис сохранил заказ в PostgreSQL и должен отправить событие об этом в Kafka. Между commit и отправкой процесс может упасть. Если поменять действия местами, возникает другой риск: событие отправлено, а транзакция с заказом откатилась.

Outbox и Inbox помогают согласовать изменения в БД с доставкой сообщений. Повторная доставка при этом остаётся возможной, но обработчики заранее готовы к ней.

<!-- more -->

<div id="the-transactional-outbox-pattern-in-python-omni-box" data-search-exclude></div>
<div id="the-dual-write-problem" data-search-exclude></div>
<div id="the-outbox-pattern" data-search-exclude></div>
<div id="using-omni-box" data-search-exclude></div>
<div id="the-inbox-side" data-search-exclude></div>
<div id="why-a-library" data-search-exclude></div>

## Сохраняем событие вместе с данными {#outbox}

В той же транзакции, где создаётся заказ, в outbox записывается событие: его постоянный идентификатор и содержимое. Обе записи либо сохраняются, либо откатываются. Поэтому репозиторий outbox не должен самостоятельно вызывать commit общей транзакции.

Отдельный отправитель (relay) читает неотправленные строки, публикует события и отмечает результат. Если он упадёт после подтверждения Kafka, но до записи отметки в БД, событие будет опубликовано снова. Идентификатор события должен оставаться тем же, чтобы потребитель мог распознать повтор.

Если отправителей несколько, нужно определить, как каждый резервирует строки для обработки и на какой срок. Эти правила должны учитывать сбои, повторные попытки и запись результата. Просто выбрать первые N строк недостаточно: другой отправитель может выбрать те же строки.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Атомарность на каждой стороне доставки</strong></figcaption>
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
    accTitle: Атомарность на каждой стороне доставки
    accDescr: Отправитель сохраняет данные и outbox одной транзакцией. Потребитель так же сохраняет изменения и отметку в inbox. Между этими шагами событие может доставляться повторно.
    A["Данные и outbox в одной транзакции"]
    B["Отправитель событий"]
    C["Kafka"]
    D["Inbox и изменения в одной транзакции"]
    E["Подтвердить обработку"]
    A --> B --> C --> D --> E
```

</div>
<p class="bdr-diagram__caption">Отправитель сохраняет данные и outbox одной транзакцией. Потребитель так же сохраняет изменения и отметку в inbox. Между этими шагами событие может доставляться повторно.</p>
</figure>
<!-- /diagram:concept -->

<div id="transactional-inbox-the-other-half-of-the-outbox-pattern" data-search-exclude></div>
<div id="the-consumers-two-problems" data-search-exclude></div>
<div id="the-inbox-row" data-search-exclude></div>
<div id="measured-the-handler-fails-halfway" data-search-exclude></div>
<div id="what-the-inbox-does-not-do" data-search-exclude></div>
<div id="the-pair" data-search-exclude></div>

## Сохраняем изменения вместе с отметкой об обработке {#inbox}

Потребитель открывает транзакцию, пытается записать идентификатор сообщения в inbox, выполняет изменения в БД и фиксирует всё вместе. Уникальное ограничение в inbox позволяет определить, было ли событие уже обработано.

Подтверждение брокеру отправляется после commit. Если процесс упадёт между этими шагами, повтор встретит готовую запись в inbox, и обработчик не выполнит изменения заново. При ошибке до commit откатятся и данные, и отметка об обработке.

В ключе записи нужно учитывать, какой обработчик получил сообщение: два независимых обработчика одного события должны иметь возможность выполнить каждый свою работу. Срок хранения inbox должен покрывать возможное повторное чтение истории событий, а не только обычные задержки доставки.

<div id="exactly-once-is-a-lie-exactly-once-effects-are-not" data-search-exclude></div>
<div id="messages-versus-effects" data-search-exclude></div>
<div id="every-window-measured" data-search-exclude></div>
<div id="the-outbox-closes-the-producer-side" data-search-exclude></div>
<div id="the-inbox-closes-the-consumer-side" data-search-exclude></div>
<div id="the-http-edge" data-search-exclude></div>
<div id="the-whole-path" data-search-exclude></div>
<div id="why-the-library-must-not-own-the-transaction" data-search-exclude></div>
<div id="what-it-looks-like" data-search-exclude></div>

## Какие действия защищает Inbox {#boundaries}

Inbox защищает только изменения в своей транзакции. Откат PostgreSQL не отменит отправленное письмо или внешний платёж. Для них нужны собственные [гарантии идемпотентности](2026-09-13-idempotency-in-apis-and-background-jobs.md).

Kafka поддерживает транзакционные сценарии внутри своей экосистемы, но их гарантии нельзя автоматически переносить на произвольную внешнюю БД. Границы описаны в разделе о [семантике доставки Kafka](https://kafka.apache.org/41/design/design/#message-delivery-semantics).

Поэтому гарантию лучше формулировать конкретно: повтор события с этим id не создаст второй счёт в данной БД. Обещание «всё exactly-once» не объясняет, на какие действия распространяется защита и что нужно проверить при сбое.

<div id="what-happens-when-kafka-is-down-for-an-hour" data-search-exclude></div>
<div id="publishing-from-the-request-path" data-search-exclude></div>
<div id="the-outbox-during-the-outage" data-search-exclude></div>
<div id="what-an-hour-actually-costs-you" data-search-exclude></div>
<div id="what-it-does-not-solve" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## Когда Kafka недоступна, события накапливаются {#outage}

Пока Kafka недоступна, приложение может продолжать сохранять данные и события в outbox, если это допускают требования продукта и хватает места в БД. Но сохранённое событие ещё не доставлено. Интерфейс не должен показывать внешнюю операцию завершённой, пока этого не произошло.

За время простоя очередь вырастет примерно на число новых событий в секунду, умноженное на длительность простоя. Чтобы разобрать накопившуюся очередь после восстановления, отправитель должен работать быстрее, чем поступают новые события. Ограничивайте повторы и отслеживайте размер очереди, возраст самого старого события и сообщения, которые не удаётся обработать.

Порядок доставки тоже нужно продумать: параллельные отправители и повторы могут его изменить. Если для сущности важна последовательность событий, выберите подходящий ключ партиции и проверяйте версии или порядковые номера событий.

## Проверяем сбой между каждым из шагов {#verification}

Имитируйте падение до commit, после commit до отправки, после отправки до записи результата и после изменений у потребителя до подтверждения брокеру. Проверьте также долгий простой, обработку накопившейся очереди и повтор старого события после очистки inbox.

[omni-box](https://bedrock-python.github.io/omni-box/) предоставляет компоненты outbox и inbox. Для их подключения сначала определите границы транзакций: где сохраняется событие, какие изменения входят в транзакцию обработчика и что подтверждается брокеру.

## Примеры и лабораторные работы {#labs}

Запускаемые примеры и инструкции к ним:

- [Практикум: как избежать повторного выполнения операции](../lab/2026-09-07-exactly-once-effects/README.md)
- [Практикум: транзакционный inbox](../lab/2026-09-07-transactional-inbox/README.md)
- [Практикум: что происходит, когда Kafka недоступна целый час](../lab/2026-09-07-when-kafka-is-down/README.md)
