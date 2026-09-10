---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - grpc-server-kit
  - grpc
  - asyncio
  - tls
  - health-checks
  - graceful-shutdown
---

# Устройство gRPC-сервера на Python для продакшена {#the-anatomy-of-a-production-python-grpc-server}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-the-anatomy-of-a-production-grpc-server" role="img" aria-label="Сервер из шести строк и набор компонентов для реальной эксплуатации" markdown="0"></div>

`grpc.aio`-сервер занимает шесть строк. Сервер, который можно поставить за балансировщиком, обновлять трижды в день и передать дежурной команде, требует набора решений, за каждым из которых стоит инцидент. Я собрал шестистрочный вариант и спросил клиента о результате. Он получил пароль БД. На вопрос Kubernetes о здоровье ответа не было. При каждом обновлении прерывался текущий платёж. Разберём компоненты, предотвращаемые ими сбои и ответы клиента с ними и без них.

<!-- more -->

Числа получены в [эксперименте статьи](../lab/2026-09-07-production-grpc-server/README.md): внутрипроцессный сервер в нескольких конфигурациях и клиент, фиксирующий статусы. Версии: grpc-server-kit 0.1.1, grpcio 1.83.1, Python 3.13.

## Обработчик выбрасывает исключение {#the-handler-that-raises}

Рано или поздно любой обработчик выбрасывает исключение, обычно с текстом для журнала. Например:

```python
async def place(self, request, context):
    raise RuntimeError(f"could not reach the ledger at {dsn}")
```

Без перехватчика отображения клиент получает:

```text
UNKNOWN: "Unexpected <class 'RuntimeError'>: could not reach the ledger at postgresql://orders:hunter2@db.internal:5432/orders"
```

Строка подключения, внутренний хост и пароль ушли вызывающей стороне. Стандартный gRPC помещает представление необработанного исключения в details: удобно отладчику, но создаёт утечку в сервисе. Статус `UNKNOWN` также не помогает политике повторов определить безопасное действие.

С отображающим исключения перехватчиком тот же обработчик возвращает:

```text
INTERNAL: 'Internal server error'
```

А исходное исключение с traceback попадает в серверный журнал. Важнее маскирования сама карта: `TimeoutError` зависимости можно отобразить в `DEADLINE_EXCEEDED` или `UNAVAILABLE` согласно контракту, а `ValueError` разбора — в `INVALID_ARGUMENT`, который не стоит повторять неизменённым. Стандартная карта покрывает обычные исключения, сервис добавляет ошибки предметной области.

Намеренные прерывания в обоих случаях проходят без изменений:

```text
PERMISSION_DENIED: 'not your order'
```

Именно так нужно: `context.abort()` передаёт осознанный статус, который не следует переписывать.

## Место перехватчика отправки ошибок {#where-the-reporting-interceptor-goes}

Список перехватчиков идёт от внешнего к внутреннему. Порядок определяет поведение. Типичная ловушка — Sentry-подобный сборщик снаружи обработчика исключений: к моменту получения исходная ошибка уже преобразована.

Эксперимент использует считающую замену Sentry и два обработчика: с `RuntimeError` и с abort `PERMISSION_DENIED`:

```text
    reporter first (outermost)   reported: ['AbortError', 'AbortError']
    reporter after the handler   reported: ['RuntimeError', 'AbortError']
```

С внешней позиции сборщик не видит исходных ошибок. Оба RPC приходят как `AbortError`, потому что внутренний слой преобразовал `RuntimeError` в abort. Трекер заполняется одинаковыми `AbortError`, без вызвавшего их бага.

Вторая строка — правильное место, но остаётся другая половина: намеренный `context.abort()` тоже выходит исключением. Сборщик, отправляющий всё, запишет каждый отказ в доступе как баг. Нужно отфильтровать abort и отправлять оставшееся.

Внутри есть ещё ловушка: `AbortError` не является `grpc.RpcError`, поэтому первый очевидный фильтр не работает:

```python
except grpc.RpcError:   # never matches a deliberate abort
```

В эксперименте оба abort попали в `except Exception`. Фильтр только по `RpcError` их не исключил.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Сначала записать исходную ошибку, затем преобразовать её</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="1" data-search-exclude>

```mermaid
---
config:
  theme: default
  look: classic
  sequence:
    useMaxWidth: false
    wrap: true
    width: 140
    actorMargin: 36
    mirrorActors: false
---
sequenceDiagram
    accTitle: Сначала записать исходную ошибку, затем преобразовать её
    accDescr: Запрос проходит обработчик исключений, затем репортёр. Ошибка идёт обратно: репортёр фиксирует исходное исключение, отфильтровывает намеренные abort, а обработчик формирует безопасный статус gRPC.
    participant C as Клиент
    participant M as Обработчик ошибок
    participant R as Репортёр
    participant H as Хендлер
    C->>M: RPC
    M->>R: Вызвать хендлер
    R->>H: Вызвать хендлер
    H-->>R: RuntimeError
    Note over R: Записать исходную, игнорировать AbortError
    R-->>M: RuntimeError
    M-->>C: INTERNAL / Internal server error
```

</div>
<p class="bdr-diagram__caption">Запрос проходит обработчик исключений, затем репортёр. Ошибка идёт обратно: репортёр фиксирует исходное исключение, отфильтровывает намеренные abort, а обработчик формирует безопасный статус gRPC.</p>
</figure>
<!-- /diagram:concept -->

## Размер сообщений {#message-size}

Стандартный предел приёма gRPC — четыре мебибайта, библиотека его сохраняет. Запрос на пять получает:

```text
RESOURCE_EXHAUSTED: 'SERVER: Received message larger than max (5242880 vs. 4194304)'
```

Разумное значение по умолчанию, но узнавать о нём в production поздно: границу пересечёт не тот payload, который был в тестах. Увеличивайте явно при законно больших сообщениях. Предел действует на сообщение с обеих сторон; клиентский предел отправки тоже должен позволять нужный размер.

Остальные значения, передаваемые в `grpc.aio.server()`, стоит один раз прочитать:

```text
    grpc.keepalive_time_ms                     7200000
    grpc.keepalive_timeout_ms                  20000
    grpc.keepalive_permit_without_calls        0
    grpc.http2.max_pings_without_data          2
    grpc.http2.min_recv_ping_interval_without_data_ms 300000
    grpc.max_metadata_size                     8192
    grpc.max_receive_message_length            4194304
    grpc.max_send_message_length               4194304
```

Два часа между keepalive — стандарт gRPC. Если балансировщик закрывает бездействующие соединения через пять минут, настройку нужно согласовать с ним. Иначе первый запрос после тишины попадёт в уже закрытое соединение и получит `UNAVAILABLE`, похожий на сетевую неисправность. Keepalive короче idle timeout помогает при соответствующей политике отправки пингов; `min_recv_ping_interval_without_data_ms` задаёт серверную сторону — слишком частые клиентские пинги считаются нарушением.

## Остановка {#shutdown}

Pod удаляется, Kubernetes запускает процедуру завершения с бюджетом `terminationGracePeriodSeconds` и отправляет `SIGTERM`. Действия сервера в этом окне решают, завершатся ли текущие запросы или превратятся в ошибки на чужом графике.

С периодом завершения сервер прекращает принимать новую работу и ждёт выполняющиеся RPC:

```text
    grace_period=5.0   stop() took 1.61 s, handler finished 1/1, client: the response arrived
```

Stop вернулся сразу после последнего обработчика, не дожидаясь полных пяти секунд. Это бюджет, не обязательная задержка.

Без такого периода:

```text
    grace_period=0.0   stop() took 0.00 s, handler finished 0/1, client: UNAVAILABLE: Cancelling all calls
```

Обработчик не завершился. Запись БД, списание или исходящий вызов прервались на текущем этапе. Клиент получил `UNAVAILABLE`, который политика повторов может счесть разрешением повторить. Так обновление способно создать повторный эффект.

Особенность gRPC: `stop(None)` означает немедленное прерывание, а не бесконечное ожидание. Настройки библиотеки требуют неотрицательное число и по умолчанию дают пять секунд. Если в низкоуровневом API передать `None` как якобы «без лимита», получится второй сценарий.

Этот период должен помещаться в бюджет pod вместе с завершением остальных компонентов. Арифметика — в [статье об остановке](2026-09-07-graceful-shutdown-is-a-protocol.md); здесь это одно слагаемое.

## Проверка здоровья {#health}

У gRPC есть протокол `grpc.health.v1.Health`, который Kubernetes умеет вызывать напрямую. Сервер без регистрации отвечает:

```text
    no enable_health(): Check -> UNIMPLEMENTED: Method not found!
```

`grpc_health_probe` завершится ошибкой, readiness уберёт pod из маршрутизации. Обратная крайность — TCP-проба, оставляющая pod доступным лишь потому, что сокет принимает соединения. Это тот же вопрос, что в [статье о Redis](2026-09-07-when-should-redis-fail-open.md): может ли сервис выполнять работу, а не только существовать.

После регистрации проверок статус следует за зависимостью:

```text
    database up:   Check -> SERVING
    database down: Check -> NOT_SERVING
    ... and the service itself still answers: OK
    database back: Check -> SERVING
```

В третьей строке БД недоступна, health сообщает `NOT_SERVING`, но RPC работает: обработчик эксперимента не обращается к БД. Слишком широкий набор проверок исключает весь pod из-за зависимости, не нужной половине методов. Разделить это помогают статусы по сервисам: `Check` принимает имя сервиса, пустое имя обозначает весь сервер.

Обратная проблема — дорогая проверка. Проверки выполняются по расписанию, результаты кешируются с TTL: ежесекундное создание соединения само нагружает защищаемую зависимость.

## TLS и права на файлы {#tls-and-the-file-permissions}

TLS требует сертификат, ключ и решение о проверке клиентов. Библиотека отказывается загружать приватный ключ, доступный кому-либо кроме владельца:

```text
    a key readable by the group: PermissionError: Sensitive file .../server.key has too permissive
    permissions (0o640). Private keys must be readable only by owner (chmod 600).
```

Это намеренная ошибка запуска: политика библиотеки требует исключить доступ других пользователей до начала обслуживания.

С исправленными правами — три типа клиента:

```text
    TLS, no client certificate required  plaintext client: UNAVAILABLE, TLS client: OK, mTLS client: OK
    mTLS, client certificate required    plaintext client: UNAVAILABLE, TLS client: UNAVAILABLE, mTLS client: OK
```

Первая строка — обычный TLS: доверяющий CA клиент подключается, незашифрованный проваливает handshake. Вторая — mTLS, где сервер требует клиентский сертификат. Клиент только с CA отклонён. Ему приходит `UNAVAILABLE`, не явное «нет сертификата», поэтому при внедрении mTLS полезен серверный журнал handshake. В stderr эксперимента причина видна ясно:

```text
Handshake failed with error SSL_ERROR_SSL: ... PEER_DID_NOT_RETURN_A_CERTIFICATE
```

Для аутентификации между сервисами mTLS проверяет идентичность на уровне соединения, не доверяя телу запроса. Авторизацию он не заменяет: отдельный перехватчик решает, какие методы доступны этой идентичности.

## Reflection и остальные компоненты {#reflection-and-the-rest-of-the-list}

Reflection позволяет `grpcurl` и Postman работать без локального `.proto`. Это удобно разработчику, но раскрывает структуру опубликованных сервисов. Библиотека требует явно указать имена для reflection, чтобы публикация была осознанной.

Остались компоненты без измерений в этой статье. Контекстный перехватчик извлекает request id из metadata и связывает с журналами. Метрики используют полное имя RPC: агрегат сервиса скрывает один медленный метод. Трассировка открывает span, но сама не читает `traceparent`: входящий контекст даёт инструментирование сервера. `max_concurrent_rpcs` ограничивает конкурентные вызовы и защищает от неограниченного роста работы и памяти при всплеске трафика.

## Порядок {#the-order}

Итоговый список от внешнего к внутреннему:

```python
interceptors = [
    AsyncMetricsInterceptor(metrics, service_name="orders"),
    AsyncContextInterceptor(header_configs),
    AsyncRequestLoggerInterceptor(),
    AsyncTracingInterceptor("orders"),
    AsyncExceptionHandlerInterceptor(),
    AsyncSentryInterceptor(),
]
```

Метрики снаружи измеряют весь вызов. Затем контекст, нужный журналам и трассировке ниже. Обработчик исключений ближе к низу, чтобы внешние слои видели статусы. Сборщик ошибок — под ним по результатам второго раздела.

Перехватчики передаются в `grpc.aio.server()` при создании. Добавить новый к уже работающему серверу нельзя, поэтому список определяется при сборке, а не расширяется поздним плагином.

## Инструменты {#the-pieces}

Это [grpc-server-kit](https://bedrock-python.github.io/grpc-server-kit/): валидация настроек до bind, загрузчик credentials с проверкой прав ключа, шесть перехватчиков в нужном порядке, health с проверками и кешем, жизненный цикл с сигналами и периодом завершения. Protobuf он не компилирует и клиентскую сторону не реализует; сгенерированные `add_*Servicer_to_server` и stubs остаются вашими.

Сервер из шести строк полезен. Просто он решает более узкую задачу, чем рабочая эксплуатация.
