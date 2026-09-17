---
date: 2026-09-13
authors:
  - alex
categories:
  - Design
tags:
  - servicewright
  - kubernetes
  - lifecycle
---

# Жизненный цикл Python-сервиса: запуск, проверки состояния и остановка {#python-service-lifecycle}

<div class="bdr-post__hero" data-bdr-post="2026-09-13-python-service-lifecycle" role="img" aria-label="Сначала вывести из маршрутизации, затем дождаться текущей работы, очистить ресурсы и выйти" markdown="0"></div>

HTTP API, обработчик сообщений Kafka и фоновые задачи могут использовать общие настройки, пул БД и внешние клиенты. Если каждая точка входа по-своему создаёт и закрывает эти ресурсы, порядок действий постепенно расходится. Правильной остановки одного обработчика недостаточно для завершения всего приложения.

Жизненный цикл стоит описать на уровне сервиса: кто создаёт и закрывает ресурсы, когда можно принимать запросы и какие операции должны завершиться перед выходом.

<!-- more -->

<div id="why-application-lifecycle-should-not-belong-to-fastapi" data-search-exclude></div>
<div id="the-api-as-usually-written" data-search-exclude></div>
<div id="the-worker-as-usually-written" data-search-exclude></div>
<div id="the-framework-is-an-entrypoint" data-search-exclude></div>
<div id="what-fastapis-lifespan-is-still-for" data-search-exclude></div>

## Отделяем ресурсы приложения от точек входа {#ownership}

Lifespan в FastAPI удобно использовать для ресурсов HTTP-приложения. Но настройки, контейнер зависимостей, пул БД и правила остановки нужны также воркерам и командам CLI. Код управления этими ресурсами должен работать независимо от веб-фреймворка.

Точка входа определяет, откуда поступают задачи: из HTTP-запросов, сообщений или расписания. Она использует подготовленные ресурсы и умеет прекращать приём новых задач. Это позволяет запускать HTTP API и воркер как вместе, так и отдельными процессами, сохраняя одинаковые правила инициализации.

<div id="one-lifecycle-for-http-grpc-workers-and-cron-jobs" data-search-exclude></div>
<div id="host-and-entrypoints" data-search-exclude></div>
<div id="one-process" data-search-exclude></div>
<div id="two-processes" data-search-exclude></div>
<div id="what-the-entrypoints-look-like" data-search-exclude></div>
<div id="the-one-thing-to-get-right" data-search-exclude></div>

## Соблюдаем порядок запуска {#startup}

Сначала проверяются настройки, затем открываются ресурсы и выполняется обязательная инициализация. Только после этого сервис сообщает, что готов принимать запросы. Если запуск прервался, уже созданные ресурсы нужно закрыть.

Для управления несколькими асинхронными ресурсами подходит `AsyncExitStack`: при открытии каждого ресурса он запоминает, как его закрыть, а при выходе закрывает их в обратном порядке. За критическими фоновыми задачами тоже нужно следить: их аварийное завершение не должно оставлять внешне исправный процесс с неработающей частью сервиса.

Прогрев нужен, если без него первый рабочий запрос получит неожиданную задержку или ошибку. При этом запуск не должен бесконечно ждать необязательный кеш. Условия готовности должны отражать реальную возможность обслуживать запросы.

<div id="warmup-readiness-and-liveness-are-three-different-things" data-search-exclude></div>
<div id="the-whole-life-of-a-pod-in-six-transitions" data-search-exclude></div>
<div id="warmup-is-not-readiness-and-neither-is-it-liveness" data-search-exclude></div>
<div id="liveness-is-about-the-process-not-the-dependencies" data-search-exclude></div>
<div id="readiness-has-to-go-false-before-the-pod-stops-serving" data-search-exclude></div>
<div id="the-three-in-one-table" data-search-exclude></div>
<div id="the-pieces" data-search-exclude></div>

## Что проверяют startup, readiness и liveness {#health}

| Проверка | Вопрос | Что включать |
|---|---|---|
| Startup | Завершилась ли начальная подготовка? | Обязательную инициализацию |
| Readiness | Можно ли направлять сюда запросы или задачи? | Состояние приложения и необходимых ему зависимостей |
| Liveness | Нужен ли перезапуск процесса? | Признаки внутренней неисправности процесса |

В Kubernetes неуспешная readiness-проверка исключает pod из обычной маршрутизации сервиса, а liveness-проверка может привести к перезапуску контейнера. Сбой общей БД обычно не исправить перезапуском всех приложений. Назначение проверок и их последствия описаны в [документации Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/).

При сбое необязательной зависимости сервис может продолжить работу с ограниченными возможностями. Например, решение о readiness при недоступном Redis зависит от его роли: кеш это или необходимое хранилище состояния.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Единый порядок запуска и остановки</strong></figcaption>
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
    accTitle: Единый порядок запуска и остановки
    accDescr: Сервис сообщает о готовности после инициализации. При остановке сначала завершаются текущие операции, затем закрываются ресурсы.
    A["Открыть ресурсы"]
    B["Прогреть зависимости"]
    C["Принимать запросы и задачи"]
    D["Выставить readiness в false"]
    E["Завершить текущие операции"]
    F["Закрыть ресурсы"]
    A --> B --> C --> D --> E --> F
```

</div>
<p class="bdr-diagram__caption">Сервис сообщает о готовности после инициализации. При остановке сначала завершаются текущие операции, затем закрываются ресурсы.</p>
</figure>
<!-- /diagram:concept -->

<div id="graceful-shutdown-in-kubernetes-is-a-protocol-not-a-signal-handler" data-search-exclude></div>
<div id="what-kubernetes-actually-does" data-search-exclude></div>
<div id="the-measurement" data-search-exclude></div>
<div id="the-protocol" data-search-exclude></div>
<div id="the-same-measurement-with-the-protocol" data-search-exclude></div>
<div id="sizing-the-numbers" data-search-exclude></div>
<div id="not-only-http" data-search-exclude></div>
<div id="what-changed-in-the-code" data-search-exclude></div>

## Остановка начинается до закрытия соединений {#shutdown}

При завершении pod маршрутизация меняется не одновременно с остановкой процесса. Часть клиентов ещё некоторое время отправляет запросы по прежнему адресу. Поэтому нужно учитывать поведение инфраструктуры: когда сервис сообщает, что больше не готов принимать запросы, и когда закрывает слушающий сокет.

Далее приложение прекращает принимать новые задачи и завершает текущие за отведённое время. Для HTTP это активные запросы, для Kafka consumer — текущая порция сообщений и фиксация позиции обработки. После этого можно закрывать клиентов, пул БД и остальные ресурсы.

В лимит `terminationGracePeriodSeconds` должны уложиться обновление маршрутизации, завершение текущих операций и освобождение ресурсов. Время выполнения `preStop` тоже входит в этот лимит. Значения выбирают с учётом длительности операций и устройства кластера.

## Проверяем весь жизненный цикл {#verification}

Полезный интеграционный тест запускает долгую операцию, отправляет процессу сигнал остановки и проверяет, что операция завершилась до закрытия её ресурсов. Второй сценарий — ошибка во время запуска: процесс должен освободить всё, что успел создать.

Отдельно проверьте медленную зависимость, аварийное завершение воркера и превышение времени на завершение текущих операций. Для каждого случая должно быть ясно, кто прекращает принимать новые задачи и что происходит с незавершёнными.

В [servicewright](https://bedrock-python.github.io/servicewright/) ресурсами управляет общий runtime, а точки входа отвечают за приём задач. Порядок остаётся единым: подготовить ресурсы, принять задачи, завершить их, освободить ресурсы.

## Примеры и лабораторные работы {#labs}

Запускаемые примеры и инструкции к ним:

- [Практикум: почему жизненный цикл приложения не должен принадлежать FastAPI](../lab/2026-09-07-lifecycle-not-fastapi/README.md)
- [Практикум: единый жизненный цикл для HTTP, планировщика и воркера](../lab/2026-09-07-one-lifecycle/README.md)
- [Практикум: прогрев и проверки startup, readiness, liveness](../lab/2026-09-07-warmup-readiness-liveness/README.md)
- [Практикум: корректное завершение — это протокол](../lab/2026-09-07-graceful-shutdown/README.md)
