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

Сервис сохранил заказ в PostgreSQL и должен сообщить о нём через Kafka. Между commit и отправкой события процесс может упасть. Если сначала отправить событие, а затем сохранить заказ, появится обратный риск: событие существует, а транзакция откатилась.

Outbox и Inbox позволяют явно организовать эти границы. Они не устраняют повторную доставку; они делают её ожидаемой частью обработки.

<!-- more -->

<div id="the-transactional-outbox-pattern-in-python-omni-box" data-search-exclude></div>
<div id="the-dual-write-problem" data-search-exclude></div>
<div id="the-outbox-pattern" data-search-exclude></div>
<div id="using-omni-box" data-search-exclude></div>
<div id="the-inbox-side" data-search-exclude></div>
<div id="why-a-library" data-search-exclude></div>

## Записать намерение вместе с данными {#outbox}

В той же транзакции, где создаётся заказ, записывается строка outbox с устойчивым event id и полезной нагрузкой. У транзакции один результат: обе записи сохранены либо обе отсутствуют. Репозиторий outbox не должен самостоятельно фиксировать чужую транзакцию.

Отдельный relay выбирает неотправленные строки, публикует их и отмечает результат. Если он упадёт после подтверждения Kafka, но до отметки в БД, событие будет опубликовано снова. Поэтому event id сохраняется между попытками, а потребитель должен распознавать повтор.

Параллельные relay требуют протокола захвата работы. Захват, срок владения, повтор после сбоя и отметка завершения должны быть согласованы; одного запроса «выбрать первые N строк» недостаточно.

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
    accDescr: Отправитель фиксирует данные и outbox вместе. Потребитель фиксирует inbox и эффект вместе; между ними событие может доставляться повторно.
    A["Данные и outbox в одной транзакции"]
    B["Relay"]
    C["Kafka"]
    D["Inbox и эффект в одной транзакции"]
    E["Подтвердить обработку"]
    A --> B --> C --> D --> E
```

</div>
<p class="bdr-diagram__caption">Отправитель фиксирует данные и outbox вместе. Потребитель фиксирует inbox и эффект вместе; между ними событие может доставляться повторно.</p>
</figure>
<!-- /diagram:concept -->

<div id="transactional-inbox-the-other-half-of-the-outbox-pattern" data-search-exclude></div>
<div id="the-consumers-two-problems" data-search-exclude></div>
<div id="the-inbox-row" data-search-exclude></div>
<div id="measured-the-handler-fails-halfway" data-search-exclude></div>
<div id="what-the-inbox-does-not-do" data-search-exclude></div>
<div id="the-pair" data-search-exclude></div>

## Зафиксировать обработку вместе с эффектом {#inbox}

Потребитель начинает транзакцию, пытается записать идентификатор сообщения в inbox, выполняет бизнес-изменение и фиксирует оба результата вместе. Уникальное ограничение отличает новую доставку от уже обработанной.

Подтверждение брокеру идёт после commit. Если процесс упадёт между ними, повторная доставка встретит существующий inbox и не повторит транзакционный эффект. Если обработчик упадёт до commit, откатятся и эффект, и отметка.

Идентификатор должен учитывать логического получателя: два независимых обработчика одного события не обязаны делить одну запись дедупликации. Срок хранения inbox согласуется с возможными replay, а не только с обычной задержкой доставки.

<div id="exactly-once-is-a-lie-exactly-once-effects-are-not" data-search-exclude></div>
<div id="messages-versus-effects" data-search-exclude></div>
<div id="every-window-measured" data-search-exclude></div>
<div id="the-outbox-closes-the-producer-side" data-search-exclude></div>
<div id="the-inbox-closes-the-consumer-side" data-search-exclude></div>
<div id="the-http-edge" data-search-exclude></div>
<div id="the-whole-path" data-search-exclude></div>
<div id="why-the-library-must-not-own-the-transaction" data-search-exclude></div>
<div id="what-it-looks-like" data-search-exclude></div>

## Явно назвать предел гарантии {#boundaries}

Inbox защищает изменения, которые входят в его транзакцию. Отправленное письмо или внешний платёж откатом PostgreSQL не отменяется. Для таких действий нужен собственный [контракт идемпотентности](2026-09-13-idempotency-in-apis-and-background-jobs.md).

Kafka поддерживает транзакционные сценарии внутри своей экосистемы, но их гарантии нельзя автоматически переносить на произвольную внешнюю БД. Границы описаны в разделе о [семантике доставки Kafka](https://kafka.apache.org/41/design/design/#message-delivery-semantics).

Поэтому полезнее описать конкретное свойство системы: повтор события с данным id не создаёт вторую запись счёта в этой БД. Формулировка «всё exactly-once» скрывает условия, которые придётся проверять при сбое.

<div id="what-happens-when-kafka-is-down-for-an-hour" data-search-exclude></div>
<div id="publishing-from-the-request-path" data-search-exclude></div>
<div id="the-outbox-during-the-outage" data-search-exclude></div>
<div id="what-an-hour-actually-costs-you" data-search-exclude></div>
<div id="what-it-does-not-solve" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## Недоступный брокер превращает отправку в очередь {#outage}

Пока Kafka недоступна, приложение может продолжать фиксировать данные и outbox, если это разрешено продуктовым контрактом и хватает места в БД. Событие сохранено, но ещё не доставлено. Пользовательский интерфейс не должен выдавать незавершённый внешний процесс за завершённый.

Размер очереди растёт примерно как скорость поступления событий, умноженная на время простоя. Для освобождения backlog после восстановления скорость relay должна превышать поступление новой работы. Ограничивайте повторные попытки и следите за возрастом самого старого события, размером очереди и неисправимыми сообщениями.

Порядок событий тоже требует решения. Несколько relay и повторные отправки могут изменить порядок наблюдения. Для сущностей, которым он важен, нужны подходящий partition key и проверяемый протокол версий или последовательности.

## Проверять каждый разрыв {#verification}

Тестируйте падение до commit, после commit перед отправкой, после отправки перед отметкой, после эффекта потребителя перед подтверждением. Проверьте длительный простой, восстановление backlog и повтор старого события после очистки inbox.

[omni-box](https://bedrock-python.github.io/omni-box/) предоставляет компоненты outbox и inbox. Их интеграция начинается с транзакционных границ приложения: где хранится намерение, где фиксируется эффект и что именно означает подтверждение.

## Примеры и лабораторные работы {#labs}

Полные стенды и условия воспроизведения вынесены в отдельные материалы:

- [Практикум: однократные эффекты](../lab/2026-09-07-exactly-once-effects/README.md)
- [Практикум: транзакционный inbox](../lab/2026-09-07-transactional-inbox/README.md)
- [Практикум: что происходит, когда Kafka недоступна целый час](../lab/2026-09-07-when-kafka-is-down/README.md)
