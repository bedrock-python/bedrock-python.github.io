---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - redis-client-kit
  - idempotency-kit
  - redis
  - reliability
  - timeouts
  - kubernetes
---

# Когда при сбое Redis стоит продолжать работу? {#when-should-redis-fail-open}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-when-should-redis-fail-open" role="img" aria-label="Недоступность зависимости одна, а решения для разных сценариев различаются" markdown="0"></div>

Redis недоступен, а он обслуживает кеш, ограничитель частоты и ключи идемпотентности. Каждый запрос должен решить, что делать. Отклонять все — превратить сбой кеша в общий отказ. Пропускать все — отключить лимиты и допустить повторное списание. Единого ответа нет и быть не должно: решение принадлежит *способу использования* Redis, а не клиенту. От клиента требуется быстро узнать о недоступности. С этого начинается измерение.

<!-- more -->

Числа получены [скриптами статьи](../lab/2026-09-07-when-should-redis-fail-open/README.md) с Redis 7, приостанавливаемым посреди запуска. Соединения не получают ни успеха, ни отказа, как при молчащем узле сети. Версии: redis-client-kit 0.1.4, idempotency-kit 0.3.0, redis-py 8.1.0, Python 3.13.

## Сначала: сколько времени нужно, чтобы узнать? {#before-deciding-anything-how-long-does-it-take-to-know}

Решение продолжать без Redis бесполезно, если принимается через десять секунд. Вместо миллисекундного кеша запрос ждёт сокет, а дедлайн клиента истекает до запасного пути. Значит, fail open требует *быстрого* отказа. Один `GET` к приостановленному Redis в разных конфигурациях:

```text
bare redis-py, defaults                                 retries=10  -> still waiting        20.00 s  (gave up watching)
bare redis-py, timeouts 0.5 + Retry(NoBackoff(), 0)     retries=0   -> TimeoutError          0.50 s
kit, timeouts 0.5, retries off (the default)            retries=0   -> TimeoutError          0.50 s
```

Стандартный клиент redis-py без таймаута сокета ждёт молчание до решения ОС — на этом ноутбуке дольше двадцати секунд наблюдения. Таймауты подключения и сокета по полсекунды кажутся исправлением, но в проверенной redis-py 8 стандартная политика добавляет до десяти попыток с экспоненциальными задержками. Полсекунды превращаются в десять–восемнадцать секунд. Быстрый результат даёт явная политика нулевых повторов — её библиотека и передаёт при отключённых retries.

Полсекунды — бюджет получения информации для всех дальнейших решений.

## Кеш: продолжить без него {#the-cache-open-always}

```text
Redis up:      cache, first lookup       -> computed                      0.05 s
               cache, second lookup      -> hit 9.99                      0.00 s
Redis paused:  cache lookup (fails open) -> computed (cache unavailable)  0.50 s
```

Промах кеша — обычный случай; запасной путь уже умеет вычислить значение. Без Redis каждый поиск становится промахом с ценой таймаута, но ответ остаётся корректным, если источник данных выдерживает нагрузку. Обратная запись в кеш тоже падает и игнорируется по той же причине. Следите за суммой ожиданий: пять обращений по полсекунды добавят 2,5 секунды. Нужны короткий таймаут и, при долгом сбое, circuit breaker, прекращающий бесполезные обращения.

## Ограничитель частоты: выбрать режим и сообщить о нём {#the-rate-limiter-open-and-say-so}

```text
Redis up:      rate limiter                   -> allowed                        0.00 s
Redis paused:  rate limiter, fail_open=True   -> allowed (limiter unavailable)  0.50 s
               rate limiter, fail_open=False  -> denied (limiter unavailable)   0.50 s
```

Без счётчика есть два варианта. Fail open временно не применяет лимит: для многих API это приемлемее запрета всех законных запросов ради защиты от возможного злоупотребления. Fail closed отклоняет запросы и нужен, если лимит — граница оплаты или защита дорогого действия. Выбор индивидуален. В обоих случаях журналируйте и считайте недоступность, чтобы период «лимит был отключён с 14:02 до 14:11» был известен, а не обнаружился загадкой в отчёте.

## Хранилище идемпотентности: цена повтора решает {#the-idempotency-store-it-depends-on-what-repeating-costs}

```text
Redis up:      idempotent charge                            -> charge_id='ch_1'   0.01 s
Redis paused:  idempotent charge, new key (fails open: runs)  -> charge_id='ch_2'   1.00 s
               idempotent charge, SAME key again (store gone) -> charge_id='ch_3'   1.01 s
               charges made while the store was gone: 2
```

Без хранилища неизвестно, встречался ли ключ. Координатор выполняет действие — компромисс доступности из [статьи об идемпотентности](2026-09-07-idempotency-keys-the-part-everyone-gets-wrong.md). Измерение показывает цену: два вызова с одним ключом дали два списания. Для сброса кеша повтор допустим; для писем это зависит от требований. Для платежа нужна дедупликация самого провайдера, поэтому ключ передаётся дальше. Если такой защиты нет, операцию стоит закрыть, вернуть допускающую поздний повтор ошибку и ждать восстановления. Координатор не знает цену действия; он считает и журналирует ошибку хранилища, а решение об отказе принимает вызывающий код.

## Здоровье: от чего зависит readiness {#health-what-readiness-should-depend-on}

```text
Redis up:      health check -> True    0.00 s
Redis paused:  health check -> False   0.50 s
```

Health возвращает false за те же полсекунды; дальше нужно решить, что это значит. Неготовый pod уходит из маршрутизации. Если так поступят все, сбой Redis станет отказом всего сервиса — fail closed на процесс. Когда все сценарии Redis допускают обход, его проверка не должна определять ни liveness, ни readiness: это метрика и тревога. При обязательном использовании готовность должна учитывать соответствующую возможность обслуживания. Часто проверку подключают к readiness просто из ощущения, что сбой нужно где-то показать. Показать можно на графике без удаления всех endpoints.

## После восстановления {#and-then-it-comes-back}

```text
Redis back:    kit GET, same client, no restart -> b'9.99'   0.00 s
               health check                     -> True      0.00 s
```

Тот же клиент работает без перезапуска и собственного переподключения приложения: пул отбрасывает испорченные соединения и открывает новые при следующей команде. Если обход работает во время аварии, но требует нового развёртывания после, восстановление ещё не завершено.

## Как выглядит решение {#the-shape}

```python
from redis_client_kit import check_async_redis_health, create_async_redis_client
from redis_client_kit.settings import BaseRedisSettings, RedisConnectionSettings, RedisPoolSettings

settings = BaseRedisSettings(
    key_prefix="shop",
    connection=RedisConnectionSettings(host="redis", port=6379),
    pool=RedisPoolSettings(socket_timeout=0.5, socket_connect_timeout=0.5),   # how long "gone" takes to notice
)                                                                            # retries off: zero, not redis-py's ten
redis = create_async_redis_client(settings)                                  # a plain redis.asyncio.Redis
```

Клиент определяет одно: сколько времени можно потратить на обнаружение отказа. Решения open или closed находятся в использующем коде с обработкой двух исключений недоступности и журналированием. [Redis-client-kit](https://bedrock-python.github.io/redis-client-kit/) собирает клиент redis-py из настроек. Начиная с 0.1.4 при отключённых повторах он передаёт явную нулевую политику; раньше не передавал ничего и получал стандартные десять.

Суть — в первой таблице: полсекунды или десять.
