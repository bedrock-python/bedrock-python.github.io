---
date: 2026-09-13
authors:
  - alex
categories:
  - Design
tags:
  - idempotency-kit
  - redis
  - idempotency
---

# Идемпотентность в API и фоновых задачах {#idempotency-in-apis-and-background-jobs}

<div class="bdr-post__hero" data-bdr-post="2026-09-13-idempotency-in-apis-and-background-jobs" role="img" aria-label="Главный случай — повтор, пришедший до завершения первого запроса" markdown="0"></div>

Клиент отправил запрос, не получил ответ и повторил его. Worker завершил задачу, но упал перед подтверждением. В обоих случаях повторная доставка нормальна; опасность появляется, когда она повторяет бизнес-действие.

Идемпотентность начинается с определения этого действия. Ключ должен обозначать намерение выполнить операцию, а не отдельную сетевую попытку или получение сообщения.

<!-- more -->

<div id="idempotency-keys-the-part-everyone-gets-wrong" data-search-exclude></div>
<div id="what-the-key-promises" data-search-exclude></div>
<div id="measured-the-request-that-is-still-running" data-search-exclude></div>
<div id="it-is-still-not-a-lock" data-search-exclude></div>
<div id="the-key-is-not-the-request" data-search-exclude></div>
<div id="failures-are-not-cached-and-neither-is-the-store" data-search-exclude></div>
<div id="scope-and-lifetime" data-search-exclude></div>
<div id="the-shape" data-search-exclude></div>

## Кеш результата не защищает выполняющуюся операцию {#reservation}

Последовательность «проверить кеш → выполнить → сохранить» пропускает два одновременных запроса: оба увидят отсутствие результата. Нужна атомарная попытка занять ключ до начала действия.

Запись обычно содержит область действия, ключ, fingerprint параметров и состояние выполнения. Победитель выполняет работу; повтор с теми же параметрами получает сохранённый результат, ждёт его ограниченное время или узнаёт, что операция ещё выполняется. Повтор с другими параметрами должен быть отклонён по явно описанному контракту.

Fingerprint не заменяет авторизацию. Область ключа должна отделять пользователей, арендаторов и разные бизнес-операции, чтобы чужой запрос не получил сохранённый ответ.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Ключ резервируется до действия</strong></figcaption>
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
    accTitle: Ключ резервируется до действия
    accDescr: Победитель атомарного резервирования выполняет действие. Повтор проверяет параметры и получает сохранённый результат либо состояние выполнения.
    A["Ключ и параметры"]
    B["Атомарное резервирование"]
    C["Выполнить действие"]
    D["Сохранить результат"]
    E["Проверить fingerprint"]
    F["Вернуть результат или статус"]
    A --> B
    B -->|"владелец"| C --> D
    B -->|"повторный вызов"| E --> F
```

</div>
<p class="bdr-diagram__caption">Победитель атомарного резервирования выполняет действие. Повтор проверяет параметры и получает сохранённый результат либо состояние выполнения.</p>
</figure>
<!-- /diagram:concept -->

<div id="idempotency-across-a-chain-of-microservices" data-search-exclude></div>
<div id="the-shape-of-the-problem" data-search-exclude></div>
<div id="the-mistake-that-looks-like-a-fix" data-search-exclude></div>
<div id="the-key-belongs-to-the-request-not-to-the-attempt" data-search-exclude></div>
<div id="the-line-that-says-the-work-is-not-finished" data-search-exclude></div>
<div id="when-there-is-no-key-to-propagate" data-search-exclude></div>
<div id="what-to-standardise-across-the-chain" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## Один ключ проходит через все попытки {#propagation}

В цепочке gateway → orders → payments новый ключ на каждом переходе не связывает повтор оплаты с исходным намерением пользователя. Ключ создают на границе операции и стабильно передают либо детерминированно преобразуют для конкретного дочернего действия.

Например, отправка счёта и списание денег по одному заказу — разные операции. Они должны иметь разные области ключа даже при общем order id. Для фоновой задачи выбирайте устойчивую идентичность действия и его версии, а не номер очередной доставки.

Успешная дедупликация не обязательно сразу даёт ответ пользователю. Если первый вызов ещё работает, API нужен понятный способ узнать результат: повтор с тем же ключом, status endpoint или идентификатор операции.

<div id="idempotency-for-background-jobs-and-kafka-consumers" data-search-exclude></div>
<div id="the-crash-before-the-ack" data-search-exclude></div>
<div id="two-workers-one-job" data-search-exclude></div>
<div id="what-the-key-is-made-of" data-search-exclude></div>
<div id="consumers-the-inbox-and-the-key-are-not-the-same-tool" data-search-exclude></div>
<div id="lifetime" data-search-exclude></div>

## Закрыть окно между эффектом и сохранением результата {#effects}

Резервирование в Redis само по себе не делает внешний платёж атомарным с записью результата. Процесс может завершить платёж и упасть до отметки о завершении. После истечения lease другой worker снова получит право работать.

Если эффект находится в той же БД, запись дедупликации и изменение данных можно объединить одной транзакцией. Для внешнего провайдера нужен стабильный ключ, который поддерживает сам провайдер, либо сверка результата и процедура восстановления. Без этого нельзя обещать однократность отправки письма или списания только благодаря локальной блокировке.

Lease должен соответствовать времени работы и правилам продления. Истечение записи не доказывает, что прежний исполнитель остановился. Эти условия особенно важны для долгих фоновых задач.

## Определить срок хранения и поведение при отказе {#failure-policy}

| Решение | Что нужно учесть |
|---|---|
| TTL результата | Максимальное окно повторов, replay и восстановления из очереди |
| Незавершённая запись | Как обнаружить и восстановить прерванную операцию |
| Ошибка действия | Можно ли безопасно повторить и какой результат показывать |
| Недоступность хранилища | Допустим ли повторный эффект без дедупликации |
| Удаление старых ключей | Что произойдёт при позднем повторе |

Автоматически удалять ключ при любом исключении опасно, если внешний эффект уже мог произойти. Так же опасно продолжать операцию без хранилища, когда её повторная стоимость неприемлема. Решение о fail-open принимается по конкретному действию.

## Проверять повторы в неудобные моменты {#verification}

Проверьте два параллельных запроса, одинаковый ключ с разными параметрами, потерю ответа, перезапуск после эффекта и до записи результата, истечение lease и сбой хранилища. Проверка только последовательного повтора уже завершённой операции недостаточна.

Для Kafka [inbox](2026-09-13-reliable-events-outbox-inbox-kafka.md) защищает транзакционные эффекты потребителя в БД. Внешнее действие остаётся отдельной границей. [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/) предоставляет координацию ключей; полный контракт операции всё равно определяется системой, которая выполняет эффект.

## Примеры и лабораторные работы {#labs}

Полные стенды и условия воспроизведения вынесены в отдельные материалы:

- [Практикум: ключи идемпотентности](../lab/2026-09-07-idempotency-keys/README.md)
- [Практикум: идемпотентность в цепочке сервисов](../lab/2026-09-07-idempotency-across-a-chain/README.md)
- [Практикум: идемпотентность фоновых задач и консьюмеров](../lab/2026-09-07-idempotency-for-jobs-and-consumers/README.md)
