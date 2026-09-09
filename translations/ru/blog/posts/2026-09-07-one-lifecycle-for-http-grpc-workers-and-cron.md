---
date: 2026-09-07
authors:
  - alex
categories:
  - Libraries
tags:
  - servicewright
  - lifecycle
  - fastapi
  - apscheduler
  - workers
  - kubernetes
---

# Один жизненный цикл для HTTP, gRPC, воркеров и cron {#one-lifecycle-for-http-grpc-workers-and-cron-jobs}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-one-lifecycle-for-http-grpc-workers-and-cron" role="img" aria-label="Общий жизненный цикл и четыре способа поступления работы" markdown="0"></div>

HTTP API, gRPC-сервер, Kafka consumer и ночная задача — одно приложение с четырьмя способами получения работы. В большинстве проектов их считают четырьмя приложениями: у API lifespan FastAPI, у consumer собственный `while True` и обработчик сигнала, у cron — `main()`, открывающий соединение БД и забывающий закрыть. У каждого своё понимание готовности и завершения. Обвязка повторяется четырежды и нигде не согласована. Альтернатива — один жизненный цикл для любого числа точек входа. Измерим, как один сервис работает одним процессом и двумя.

<!-- more -->

Временные шкалы получены в [эксперименте статьи](../lab/2026-09-07-one-lifecycle/README.md): одно определение сервиса, три способа запуска, печать каждого вызова жизненного цикла. Версии: servicewright 0.10.0, FastAPI 0.141.1, uvicorn 0.52.4, APScheduler 4.0.0a6, Python 3.13.

## Host и точки входа {#host-and-entrypoints}

В модели две сущности. **Точка входа** — способ получения работы: HTTP-сервер, gRPC-сервер, планировщик, опрос очереди, одноразовая задача. Каждая отвечает на четыре вызова: `bind` выделяет ресурсы и подписывается, но не принимает трафик; `serve` работает до сигнала остановки и возвращается, ещё сохраняя приём; `drain` прекращает приём и завершает текущую работу в пределах бюджета; `stop` окончательно останавливает. **Host** вызывает эти методы в фиксированном порядке у всех переданных точек входа, не интересуясь их типом.

Вокруг — общие настройки, контейнер зависимостей с областью приложения и отдельной единицы работы, прогрев до готовности, реестр здоровья, наблюдаемость и бюджеты завершения. Всё принадлежит сервису и объявляется один раз в spec:

```python
spec = AppSpec(
    service_name="orders",
    create_container=lambda settings: Container(),
    drain_delay_seconds=0.3,
    drain_grace_seconds=5.0,
)
ENTRYPOINTS = {"all": [api, cron, worker], "api": [api], "worker": [cron, worker]}
run_sync(Service(spec, entrypoints=ENTRYPOINTS[role]), Settings())
```

В эксперименте три точки входа: FastAPI с одним маршрутом, задача APScheduler каждые полсекунды и фоновый цикл вместо consumer. Все используют один пул через контейнер; роль определяет, какие точки запустит процесс.

## Один процесс {#one-process}

Сервис запущен с ролью `all`, получает работу секунду, затем `SIGTERM`:

```text
 0.02 s  pool opened
 0.02 s  bind    http
 0.02 s  bind    scheduler
 0.03 s  bind    daemon
 0.03 s  ready = true, post_start hook
 0.03 s  serve   http
 0.03 s  serve   scheduler
 0.03 s  serve   daemon
 0.03 s  worker loop used the pool (use #1)
 0.59 s  scheduled job used the pool (use #3)
 0.59 s  http request used the pool (use #4)
 1.02 s  scheduled job used the pool (use #7)
 1.03 s  http request used the pool (use #8)
 1.23 s  serve   scheduler returned (still accepting)
 1.23 s  worker loop saw the stop event and finished its batch
 1.23 s  serve   daemon returned (still accepting)
 1.23 s  serve   http returned (still accepting)
 1.52 s  scheduled job used the pool (use #9)
 1.54 s  drain   daemon
 1.54 s  drain   scheduler
 1.54 s  drain   http
 1.71 s  stop    daemon
 1.71 s  stop    scheduler
 1.71 s  stop    http
 1.71 s  pre_shutdown hook, app scope still open
 1.71 s  pool closed
 exit code 0
```

Читайте сверху вниз: смысл в порядке. Пул открывается один раз до первого использования. Три точки выполняют bind в порядке списка; readiness становится true только после последнего bind. Балансировщик видит готовый сервис, у которого уже работают и планировщик, и worker. Все три выполняются конкурентно через один пул; счётчик показывает чередование запросов, задач и итераций.

Затем сигнал. Все `serve` возвращаются, обёртка печатает «still accepting»: планировщик ещё активен, worker завершил текущий пакет, HTTP-сокет открыт. Readiness уже false, но ещё три десятых секунды процесс обслуживает поступающее; поэтому планировщик срабатывает снова на 1,52 с. Это окно из [статьи об остановке](2026-09-07-graceful-shutdown-is-a-protocol.md). Затем drain в *обратном* порядке bind: daemon, планировщик, HTTP-сервер — как разворачивание стека. Потом stop в том же порядке, обработчик перед завершением с ещё открытой областью приложения, где outbox может отправить остаток. Лишь затем закрывается пул: он уже никому не нужен. Выход с кодом ноль.

Точки входа не знают друг о друге и о сроке жизни пула. Порядок задаёт Host.

## Два процесса {#two-processes}

Тот же файл и spec запускаются дважды с разными ролями. Сначала `api`:

```text
 0.01 s  pool opened
 0.01 s  bind    http
 0.01 s  ready = true, post_start hook
 0.01 s  serve   http
 0.02 s  http request used the pool (use #1)
 0.46 s  http request used the pool (use #3)
 0.67 s  serve   http returned (still accepting)
 0.97 s  drain   http
 1.14 s  stop    http
 1.14 s  pre_shutdown hook, app scope still open
 1.14 s  pool closed
 exit code 0
```

Затем `worker`:

```text
 0.01 s  pool opened
 0.01 s  bind    scheduler
 0.02 s  bind    daemon
 0.02 s  ready = true, post_start hook
 0.02 s  serve   scheduler
 0.02 s  serve   daemon
 0.02 s  worker loop used the pool (use #1)
 0.51 s  scheduled job used the pool (use #4)
 0.93 s  serve   scheduler returned (still accepting)
 0.93 s  worker loop saw the stop event and finished its batch
 0.93 s  serve   daemon returned (still accepting)
 1.23 s  drain   daemon
 1.23 s  drain   scheduler
 1.23 s  stop    daemon
 1.23 s  stop    scheduler
 1.23 s  pre_shutdown hook, app scope still open
 1.23 s  pool closed
 exit code 0
```

К такому развёртыванию приходит большинство сервисов: API масштабируется по частоте запросов, worker — по глубине очереди, со своими лимитами ресурсов и числом реплик. Обычно разделение стоит второй кодовой базы или второго `main()` с копией запуска и остановки. Копии расходятся, пока worker не начинает терять сообщения при обновлении. Здесь понадобился один словарь. Контейнер, прогрев, проверки здоровья, бюджеты и порядок одинаковы в обоих процессах: точки входа их никогда не определяли.

У worker нет HTTP-сервера, но readiness есть: переключается после обоих bind. Развёртывание Kubernetes с exec-пробой или небольшой дополнительной точкой здоровья получит тот же сигнал, что API. Готовность тоже не является исключительно HTTP-понятием.

## Как выглядят точки входа {#what-the-entrypoints-look-like}

Фоновый цикл consumer или poller — функция от области единицы работы и события остановки:

```python
async def consume(scope, stop: asyncio.Event) -> None:
    pool = await scope.get("pool")
    while not stop.is_set():
        await pool.use("worker loop")
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=0.4)

worker = DaemonEntrypoint(consume)
```

Задача по расписанию — функция от области единицы работы; точка входа открывает новую область на каждый запуск:

```python
async def nightly_report(scope) -> None:
    await (await scope.get("pool")).use("scheduled job")

cron = SchedulerEntrypoint(jobs=[ScheduledJob(id="report", func=nightly_report, trigger=IntervalTrigger(seconds=0.5))])
```

HTTP-сервер — обычное приложение FastAPI, чьи маршруты получают область работы как зависимость. Middleware точки входа открывает её на запрос, маршрут не видит контейнер:

```python
@router.get("/work")
async def work(unit: UnitScopeDep) -> dict[str, str]:
    await (await unit.get("pool")).use("http request")
    return {"status": "ok"}

api = FastApiEntrypoint(config=HttpConfig(port=8000), routers=(router,))
```

Три разных способа поступления работы и одинаковые ответы на два вопроса: откуда берётся область зависимостей и как остановиться. gRPC-сервер — четвёртый вариант, помещающийся в тот же список.

## Главное правило {#the-one-thing-to-get-right}

Каждая точка должна возвращаться из `serve`, ещё сохраняя возможность принимать работу, и оставлять закрытие методу `drain`. Здесь легко ошибиться: стандартная остановка фреймворка объединяет оба действия. Если сделать это в `serve`, исчезнет окно между выключением readiness и закрытием приёма. Четыре метода позволяют Host управлять этим окном сразу за все точки входа. Поэтому первая временная шкала — одна последовательность вместо трёх независимых.

Этот Host — [servicewright](https://bedrock-python.github.io/servicewright/concepts/entrypoints/), предоставляющий точки входа FastAPI, Litestar, gRPC, APScheduler, daemon и one-shot. Он проводит выбранный набор через Bootstrap, Warmup, Ready, Serve, Drain и Cleanup.

Суть — в двух строках `pool closed`: по одной в каждом процессе, обе в самом конце.
