---
title: Блог
description: "Практические статьи о Python в эксплуатации: PostgreSQL, gRPC, Kafka, жизненный цикл сервисов и отказоустойчивые системы."
hide:
  - navigation
  - toc
---

<div class="bdr-explorer" data-blog-explorer data-catalog-url="catalog.json" data-view="list" markdown="0">
  <header class="bdr-journal">
    <div>
      <div class="bdr-journal__eyebrow"><span></span> БЛОГ BEDROCK</div>
      <h1>Инженерия за пределами<br> <em>идеального сценария.</em></h1>
      <p>Заметки о системах на Python, которые выдерживают реальные нагрузки.<br class="bdr-desktop-break"> Решения, компромиссы и код, который за ними стоит.</p>
    </div>
    <div class="bdr-journal__aside" aria-hidden="true">
      <svg viewBox="0 0 130 100" fill="none"><path d="M65 8 112 33 65 58 18 33 65 8Z"/><path d="m18 48 47 25 47-25M18 63l47 25 47-25"/><path d="M65 58v30M18 33v30M112 33v30"/><path class="bdr-journal__accent" d="m65 8 47 25-47 25-47-25L65 8Z"/></svg>
      <span>ИЗ МИРА<br>ИНФРАСТРУКТУРЫ</span>
    </div>
  </header>

  <div class="bdr-discovery" data-blog-controls hidden>
    <div class="bdr-searchbox" role="search" aria-label="Поиск по статьям блога">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></svg>
      <label class="bdr-sr-only" for="blog-query">Поиск статей по названию, теме или библиотеке</label>
      <input id="blog-query" data-blog-query type="search" placeholder="Найти статью, тему, библиотеку…" autocomplete="off" spellcheck="false" enterkeyhint="search" aria-controls="blog-results">
      <button class="bdr-searchbox__clear" data-blog-clear-query type="button" aria-label="Очистить поиск" hidden>×</button>
      <kbd aria-hidden="true">/</kbd>
    </div>
    <span class="bdr-discovery__hint">Есть конкретная задача? Начните здесь.</span>
  </div>
  <p class="bdr-load-status" data-blog-load-status role="status">Все статьи доступны ниже. <a href="archive/">Открыть архив →</a></p>

  <section class="bdr-collections" aria-labelledby="collections-title">
    <div class="bdr-collections__heading"><h2 id="collections-title">С чего начать</h2><span>Выберите интересную тему</span></div>
    <div class="bdr-collections__grid">
      <a class="bdr-collection bdr-collection--resilience" data-blog-collection="reliability" href="posts/2026-09-06-timeouts-are-not-deadlines/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><rect x="4" y="16" width="12" height="16" rx="3"/><rect x="32" y="16" width="12" height="16" rx="3"/><path d="M16 24h16m-11-5 5 5-5 5M10 10V6m28 36v-4"/></svg></div>
        <div><span class="bdr-collection__label">КОГДА ЗАВИСИМОСТИ ПОДВОДЯТ</span><h3>Создавайте надёжные сервисы</h3><p>Дедлайны, повторы и circuit breaker</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--postgres" data-blog-collection="postgres" href="posts/2026-09-13-postgresql-partition-maintenance/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><ellipse cx="24" cy="11" rx="15" ry="6"/><path d="M9 11v25c0 3.3 6.7 6 15 6s15-2.7 15-6V11M9 23c0 3.3 6.7 6 15 6s15-2.7 15-6M9 35c0 3.3 6.7 6 15 6s15-2.7 15-6"/></svg></div>
        <div><span class="bdr-collection__label">ЗА ПРЕДЕЛАМИ ЗАПРОСА</span><h3>Postgres в эксплуатации</h3><p>Секции, сессии и миграции</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--messaging" data-blog-collection="messaging" href="posts/2026-09-13-reliable-events-outbox-inbox-kafka/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><rect x="3" y="18" width="10" height="12" rx="2"/><rect x="35" y="18" width="10" height="12" rx="2"/><rect x="19" y="6" width="10" height="12" rx="2"/><rect x="19" y="30" width="10" height="12" rx="2"/><path d="m13 24 6-12m10 0 6 12m-22 0 6 12m10 0 6-12"/></svg></div>
        <div><span class="bdr-collection__label">КАЖДОЕ СОБЫТИЕ ВАЖНО</span><h3>Доставляйте сообщения надёжно</h3><p>Kafka, Outbox и однократные эффекты</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
    </div>
  </section>

  <div class="bdr-explorer__layout">
    <aside class="bdr-explorer__sidebar" data-blog-controls hidden>
      <details class="bdr-topics" data-blog-topics-panel open>
        <summary>Выбрать тему <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m5 7 5 5 5-5"/></svg></summary>
        <nav aria-label="Темы статей" class="bdr-topics__nav">
          <button data-blog-topic="all" type="button" aria-pressed="true"><span class="bdr-topic-symbol" aria-hidden="true">✳</span><span>Все статьи</span><span data-topic-count></span></button>
          <button data-blog-topic="postgres" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">▤</span><span>PostgreSQL и SQLAlchemy</span><span data-topic-count></span></button>
          <button data-blog-topic="reliability" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">↻</span><span>HTTP и отказоустойчивость</span><span data-topic-count></span></button>
          <button data-blog-topic="grpc" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">⇄</span><span>gRPC</span><span data-topic-count></span></button>
          <button data-blog-topic="messaging" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">⇢</span><span>Kafka и обмен сообщениями</span><span data-topic-count></span></button>
          <button data-blog-topic="lifecycle" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">◷</span><span>Жизненный цикл сервиса</span><span data-topic-count></span></button>
          <button data-blog-topic="redis" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">◇</span><span>Redis и идемпотентность</span><span data-topic-count></span></button>
          <button data-blog-topic="engineering" type="button" aria-pressed="false"><span class="bdr-topic-symbol" aria-hidden="true">⌘</span><span>Python и инструменты</span><span data-topic-count></span></button>
        </nav>
      </details>
      <div class="bdr-explorer__note"><span>ДЕЛИМСЯ ОПЫТОМ</span><p>Реальные задачи эксплуатации.<br>Рабочий код. Практические выводы.</p><a href="archive/">Полный архив <span aria-hidden="true">↗</span></a></div>
    </aside>

    <section class="bdr-explorer__main" aria-labelledby="blog-results-heading">
      <div class="bdr-results-heading" data-blog-results-heading>
        <div><h2 id="blog-results-heading" tabindex="-1">Статьи</h2><span data-blog-count role="status" aria-live="polite" aria-atomic="true">Заметки об инфраструктуре</span></div>
        <div class="bdr-view-switch" role="group" aria-label="Вид списка статей" data-blog-controls hidden>
          <button data-blog-view="list" type="button" aria-label="Список" title="Список" aria-pressed="true"><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M7 5h10M7 10h10M7 15h10M3 5h.5M3 10h.5M3 15h.5"/></svg></button>
          <button data-blog-view="grid" type="button" aria-label="Сетка" title="Сетка" aria-pressed="false"><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="3" y="3" width="5" height="5" rx=".5"/><rect x="12" y="3" width="5" height="5" rx=".5"/><rect x="3" y="12" width="5" height="5" rx=".5"/><rect x="12" y="12" width="5" height="5" rx=".5"/></svg></button>
        </div>
      </div>
      <div class="bdr-toolbar" data-blog-controls hidden>
        <div class="bdr-toolbar__filters">
          <label><span class="bdr-sr-only">Формат статьи</span><select data-blog-format aria-controls="blog-results"><option value="all">Все форматы</option><option value="design">Архитектура</option><option value="tutorials">Руководства</option><option value="libraries">Библиотеки</option><option value="tools">Инструменты</option><option value="meta">Об экосистеме</option></select></label>
          <label><span class="bdr-sr-only">Время чтения</span><select data-blog-duration aria-controls="blog-results"><option value="all">Любая длительность</option><option value="short">До 8 минут</option><option value="long">Более 8 минут</option></select></label>
        </div>
        <label class="bdr-toolbar__sort"><span>Порядок:</span><select data-blog-sort aria-label="Сортировка статей" aria-controls="blog-results"><option value="newest">Сначала новые</option><option value="oldest">Сначала старые</option><option value="shortest">Сначала короткие</option><option value="title">По алфавиту</option></select></label>
      </div>
      <div class="bdr-active-filters" data-blog-active hidden></div>
      <div class="bdr-results" id="blog-results" data-blog-results>
<!-- catalog:articles:start -->
  <article class="bdr-entry" data-article-id="2026-09-13-kafka-in-python-services">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-kafka-in-python-services/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Kafka в Python-сервисе: producer, consumer и эксплуатация</h3>
        <p class="bdr-entry__description">Kafka-клиент должен вписываться в правила сервиса: кто владеет топиками, когда сообщение считается обработанным и что происходит при остановке.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-python-library-from-template-to-release">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-python-library-from-template-to-release/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Python-библиотека от шаблона до релиза</h3>
        <p class="bdr-entry__description">При работе с несколькими Python-библиотеками повторяется не только код. В каждом репозитории нужны сборка, тесты, правила форматирования, документация и выпуск на PyPI.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-redis-failures-and-health-checks">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-redis-failures-and-health-checks/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Redis недоступен: health checks и поведение сервиса</h3>
        <p class="bdr-entry__description">Redis может обслуживать кэш, ограничивать частоту запросов и хранить ключи идемпотентности в одном сервисе. При его отказе этим операциям нужны разные правила.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-sqlalchemy-pgbouncer-pools">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-sqlalchemy-pgbouncer-pools/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">SQLAlchemy и PgBouncer: настройка и диагностика пула соединений</h3>
        <p class="bdr-entry__description">Пул соединений полностью занят, но приложение отвечает быстро. После замедления БД тот же график показывает те же занятые соединения, а запросы уже завершаются по таймауту.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-python-service-lifecycle">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-python-service-lifecycle/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Жизненный цикл Python-сервиса: запуск, health checks и остановка</h3>
        <p class="bdr-entry__description">У HTTP API, Kafka consumer и фоновой задачи могут быть общие настройки, пул БД и внешние клиенты.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-why-bedrock-python-libraries">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-why-bedrock-python-libraries/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Зачем я выделяю инфраструктуру Python-сервисов в библиотеки</h3>
        <p class="bdr-entry__description">В Python-сервисах на одном стеке я снова и снова собирал похожую инфраструктуру: сессии SQLAlchemy, клиентов Redis и Kafka, запуск и остановку ресурсов, повторные запросы…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-idempotency-in-apis-and-background-jobs">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-idempotency-in-apis-and-background-jobs/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Идемпотентность в API и фоновых задачах</h3>
        <p class="bdr-entry__description">Клиент отправил запрос, не получил ответ и повторил его. Worker завершил задачу, но упал перед подтверждением.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-partitioning-an-existing-postgresql-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-partitioning-an-existing-postgresql-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Как перевести таблицу PostgreSQL на партиционирование</h3>
        <p class="bdr-entry__description">Перевод существующей таблицы на партиционирование меняет больше, чем способ хранения строк.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-production-python-grpc-server">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-production-python-grpc-server/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Как подготовить Python gRPC-сервер к продакшену</h3>
        <p class="bdr-entry__description">Зарегистрировать servicer и открыть порт достаточно для первого gRPC-вызова. Для эксплуатации нужно определить поведение сервера вокруг обработчика: какие ошибки увидит клиент…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-testing-alembic-migrations-in-ci">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-testing-alembic-migrations-in-ci/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Как проверять миграции Alembic в CI</h3>
        <p class="bdr-entry__description">Успешный alembic upgrade head проверяет только один путь: применение истории к выбранному исходному состоянию.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-production-http-grpc-clients">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-production-http-grpc-clients/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Как строить HTTP- и gRPC-клиенты для продакшена</h3>
        <p class="bdr-entry__description">Клиент внешнего сервиса должен ограничивать стоимость неудачного вызова: время ожидания, число попыток и нагрузку на зависимость. Эти решения связаны.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-reliable-events-outbox-inbox-kafka">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-reliable-events-outbox-inbox-kafka/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Надёжная доставка событий: Outbox, Inbox и сбои Kafka</h3>
        <p class="bdr-entry__description">Сервис сохранил заказ в PostgreSQL и должен сообщить о нём через Kafka. Между commit и отправкой события процесс может упасть.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-postgresql-partition-maintenance">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-postgresql-partition-maintenance/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Обслуживание партиций PostgreSQL: создание, архивирование и удаление</h3>
        <p class="bdr-entry__description">Создать следующую партицию сравнительно просто. Эксплуатационная сложность появляется вокруг неё: кто отвечает за расписание, какие таблицы можно удалять, что делать при сбое…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-ai-code-review-should-not-be-fully-autonomous">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-ai-code-review-should-not-be-fully-autonomous/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Инструменты</div>
        <h3 class="bdr-entry__title">Почему ревью с ИИ нужно контролировать</h3>
        <p class="bdr-entry__description">ИИ помог мне находить ошибки в собственных merge request. Проблемы начались, когда я стал автоматизировать ревью кода коллег: полезные находки смешивались с неверными замечаниями…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-13-sqlalchemy-sessions-and-transactions">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-13-sqlalchemy-sessions-and-transactions/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Сессии и транзакции в SQLAlchemy: кто владеет commit</h3>
        <p class="bdr-entry__description">Заказ и событие о его создании должны появиться вместе. Если каждый репозиторий самостоятельно вызывает commit(), ошибка записи события оставляет заказ без события.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-documentation-for-ai-coding-agents">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-documentation-for-ai-coding-agents/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Мы начали писать документацию для ИИ-агентов</h3>
        <p class="bdr-entry__description">В 2024 году я писал документацию для разработчиков. В какой-то момент 2026-го заметил, что значительная часть читателей — не люди.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-why-grpc-interceptors-break-on-streaming-rpcs/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Почему перехватчики gRPC ломаются на потоковых RPC</h3>
        <p class="bdr-entry__description">Перехватчик, измеряющий вызов, считающий ошибки и связывающий request id, занимает двадцать строк и работает.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-zero-dependency-cores">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-zero-dependency-cores/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Ядро без зависимостей: зачем инфраструктурным библиотекам необязательные зависимости</h3>
        <p class="bdr-entry__description">Инфраструктурная библиотека попадает во многие сервисы вместе со всеми своими зависимостями. Обычно об этом рассуждают отвлечённо.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-06-timeouts-are-not-deadlines">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-06-timeouts-are-not-deadlines/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Таймаут — не дедлайн: как теряется бюджет времени в микросервисах</h3>
        <p class="bdr-entry__description">Представим сервис Orders: он получает остатки по HTTP, затем резервирует товар и списывает оплату через gRPC.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-06">6 сент. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
<!-- catalog:articles:end -->
      </div>
      <div class="bdr-empty" data-blog-empty hidden>
        <span class="bdr-empty__icon" aria-hidden="true">⌕</span><h3>Статьи не найдены. Попробуем иначе?</h3>
        <p>Попробуйте более общий запрос, например «повторы» или «PostgreSQL», либо сбросьте фильтры.</p>
        <button class="bdr-btn bdr-btn--primary" type="button" data-blog-reset>Сбросить все фильтры</button>
      </div>
      <footer class="bdr-results-footer" data-blog-controls hidden>
        <span data-blog-range></span><nav class="bdr-pagination" aria-label="Страницы списка статей" data-blog-pagination></nav>
      </footer>
    </section>
  </div>
</div>
