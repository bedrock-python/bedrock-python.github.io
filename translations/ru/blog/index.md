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
      <a class="bdr-collection bdr-collection--postgres" data-blog-collection="postgres" href="posts/2026-09-06-pg-partsmith/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><ellipse cx="24" cy="11" rx="15" ry="6"/><path d="M9 11v25c0 3.3 6.7 6 15 6s15-2.7 15-6V11M9 23c0 3.3 6.7 6 15 6s15-2.7 15-6M9 35c0 3.3 6.7 6 15 6s15-2.7 15-6"/></svg></div>
        <div><span class="bdr-collection__label">ЗА ПРЕДЕЛАМИ ЗАПРОСА</span><h3>Postgres в эксплуатации</h3><p>Секции, сессии и миграции</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--messaging" data-blog-collection="messaging" href="posts/2026-05-15-transactional-outbox-with-omni-box/">
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
  <article class="bdr-entry" data-article-id="2026-09-07-circuit-breakers-should-be-per-origin">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-circuit-breakers-should-be-per-origin/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Circuit breaker должен быть отдельным для каждого origin, а не клиента</h3>
        <p class="bdr-entry__description">Circuit breaker проще всего объяснить и проще всего привязать не к тому ключу. Объяснение помещается в предложение: после достаточного числа сбоев ненадолго прекратить вызовы…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">PgBouncer в режиме транзакций и асинхронный SQLAlchemy: рабочая конфигурация, которой не хватает в документации</h3>
        <p class="bdr-entry__description">Конфигурация SQLAlchemy прекрасно работает напрямую с PostgreSQL. Затем перед БД ставят PgBouncer в режиме транзакций, ради которого обычно и нужен пулер, и прежние предположения…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-retry-after-backoff-and-jitter">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-retry-after-backoff-and-jitter/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Retry-After, backoff и jitter: что делает HTTP-клиент в продакшене</h3>
        <p class="bdr-entry__description">Обычный цикл повторов — четыре строки: попытаться, поймать, подождать, повторить. Рабочая политика HTTP-клиента требует примерно восьми решений, которые этот цикл молча принимает…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-uuidv7-as-a-postgresql-partition-key">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-uuidv7-as-a-postgresql-partition-key/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">UUIDv7 как ключ партиционирования PostgreSQL</h3>
        <p class="bdr-entry__description">Диапазонное партиционирование по времени обычно требует изменить первичный ключ: PostgreSQL требует включить колонку партиционирования во все уникальные ограничения.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-safe-grpc-retries">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-safe-grpc-retries/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Безопасные повторы gRPC: какие статусы действительно стоит повторять</h3>
        <p class="bdr-entry__description">max_attempts=3 — самая частая и редко осмысленная строка gRPC-конфигурации. Повтор — ставка на то, что сервер ещё не сделал работу и повторение ничего не стоит.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-twelve-libraries-one-standard">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-twelve-libraries-one-standard/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Двенадцать библиотек, один инженерный стандарт, без монорепозитория</h3>
        <p class="bdr-entry__description">Bedrock Python — шестнадцать репозиториев: двенадцать библиотек, два инструмента, шаблон и этот сайт.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-should-your-application-create-kafka-topics-on-startup">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-should-your-application-create-kafka-topics-on-startup/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Должно ли приложение создавать топики Kafka при запуске?</h3>
        <p class="bdr-entry__description">Кто-то должен создать топик. Кандидатов три: брокер автоматически при первом упоминании имени, приложение при запуске или человек через процесс управления кластером.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-exactly-once-effects">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-exactly-once-effects/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Доставка exactly-once — миф; однократные эффекты реальны</h3>
        <p class="bdr-entry__description">Kafka не может гарантировать ровно одно обновление вашей БД. Без общей транзакции этого не может гарантировать ни один брокер: база и брокер — две системы с двумя фиксациями, и…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-idempotency-across-a-chain-of-microservices">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-idempotency-across-a-chain-of-microservices/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Идемпотентность в цепочке микросервисов</h3>
        <p class="bdr-entry__description">Один ключ идемпотентности в одном сервисе — решённая задача. В цепочке всё сложнее: важный повтор происходит наверху, важный эффект — внизу, а между ними два–три перехода с…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-idempotency-for-jobs-and-consumers">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-idempotency-for-jobs-and-consumers/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Идемпотентность фоновых задач и консьюмеров Kafka</h3>
        <p class="bdr-entry__description">Заголовок Idempotency-Key привлекает внимание, потому что у него есть имя и спецификация. Но та же проблема возникает у каждого worker очереди, причём чаще: очереди по своей…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-mapping-python-exceptions-to-grpc-status-codes">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-mapping-python-exceptions-to-grpc-status-codes/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Как отображать исключения Python в статусы gRPC без утечки внутренних данных</h3>
        <p class="bdr-entry__description">У gRPC шестнадцать кодов ошибок помимо успешного статуса, а у вашего сервиса сотня типов исключений: кому-то нужно задать соответствие.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-how-to-partition-an-existing-postgresql-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-how-to-partition-an-existing-postgresql-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Как партиционировать существующую таблицу PostgreSQL без переписывания приложения</h3>
        <p class="bdr-entry__description">ALTER TABLE ... PARTITION BY не существует. Чтобы сделать рабочую таблицу партиционированной, нужно создать нового родителя, присоединить старую таблицу как DEFAULT-партицию и…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-how-i-start-a-production-grade-python-library">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-how-i-start-a-production-grade-python-library/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Как я начинаю разработку Python-библиотеки для продакшена в 2026 году</h3>
        <p class="bdr-entry__description">Каждая библиотека этой серии начиналась одинаково: одна команда, сорок один файл и зелёные проверки примерно через три секунды. Речь о распределении усилий.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-idempotency-keys-the-part-everyone-gets-wrong">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-idempotency-keys-the-part-everyone-gets-wrong/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Ключи идемпотентности: часть, которую обычно реализуют неправильно</h3>
        <p class="bdr-entry__description">Idempotency-Key — одна из самых копируемых и чаще всего неправильно реализуемых идей платёжных API.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-when-should-redis-fail-open">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-when-should-redis-fail-open/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Когда при сбое Redis стоит продолжать работу?</h3>
        <p class="bdr-entry__description">Redis недоступен, а он обслуживает кеш, ограничитель частоты и ключи идемпотентности. Каждый запрос должен решить, что делать. Отклонять все — превратить сбой кеша в общий отказ.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-graceful-shutdown-is-a-protocol">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-graceful-shutdown-is-a-protocol/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Корректная остановка в Kubernetes — это протокол, а не обработчик сигнала</h3>
        <p class="bdr-entry__description">Каждый веб-фреймворк обрабатывает SIGTERM: прекращает принимать соединения, даёт текущим запросам завершиться и аккуратно выходит.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-graceful-kafka-consumer-shutdown">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-graceful-kafka-consumer-shutdown/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Корректная остановка консьюмера Kafka в Kubernetes</h3>
        <p class="bdr-entry__description">Kafka consumer в Kubernetes развёртывается заново несколько раз в день, и каждый раз получает SIGTERM посреди пакета.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-your-models-and-your-schema-have-drifted">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-your-models-and-your-schema-have-drifted/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Модели и схема БД разошлись. Заметит ли CI?</h3>
        <p class="bdr-entry__description">Миграция прошла, развёртывание завершилось, модели и БД теперь утверждают разное. Ошибки нет: обычный alembic upgrade head на пустой БД не проверяет соответствие результата…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
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
  <article class="bdr-entry" data-article-id="2026-09-07-reliability-is-not-retry-3">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-reliability-is-not-retry-3/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Надёжность — это не retry=3</h3>
        <p class="bdr-entry__description">retry=3 первым добавляют в HTTP-клиент и последним пересматривают. Это одна настройка, а не стратегия надёжности. В обычный день она незаметна, поэтому переживает любое ревью.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-one-lifecycle-for-http-grpc-workers-and-cron">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-one-lifecycle-for-http-grpc-workers-and-cron/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Библиотеки</div>
        <h3 class="bdr-entry__title">Один жизненный цикл для HTTP, gRPC, воркеров и cron</h3>
        <p class="bdr-entry__description">HTTP API, gRPC-сервер, Kafka consumer и ночная задача — одно приложение с четырьмя способами получения работы.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-transport-independent-errors">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-transport-independent-errors/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Ошибки без привязки к транспорту: одна ошибка предметной области, ответы HTTP и gRPC</h3>
        <p class="bdr-entry__description">Сервис с внешним HTTP и внутренним gRPC формирует два ответа на каждый сбой, и они расходятся.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-unit-of-work-in-sqlalchemy-2">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-unit-of-work-in-sqlalchemy-2/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Паттерн Unit of Work в SQLAlchemy 2</h3>
        <p class="bdr-entry__description">Почти каждый впервые написанный репозиторий содержит commit(): чтобы получить id, передать его дальше, прочитать строку в тесте.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-stop-passing-asyncsession-everywhere">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-stop-passing-asyncsession-everywhere/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Перестаньте передавать AsyncSession повсюду</h3>
        <p class="bdr-entry__description">Во всех проектах с async SQLAlchemy, где я работал, на каждом уровне повторялась одна сигнатура:</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-migrating-from-pg-partman">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-migrating-from-pg-partman/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Переход с pg_partman на управление партициями из приложения</h3>
        <p class="bdr-entry__description">pg_partman — стандартный и хороший ответ на обслуживание партиций PostgreSQL, когда доступны расширения и команда готова управлять логикой внутри БД.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-retries-can-make-an-outage-worse">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-retries-can-make-an-outage-worse/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Повторы могут усугубить сбой: проектируем бюджет повторных попыток</h3>
        <p class="bdr-entry__description">Три попытки на каждом переходе цепочки из пяти сервисов — усилитель нагрузки, который сильнее всего действует именно при сбое нижнего сервиса, когда тот меньше всего способен…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-partition-retention-is-not-drop-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-partition-retention-is-not-drop-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Политика хранения партиций — это не DROP TABLE</h3>
        <p class="bdr-entry__description">Задача очистки — та строка настройки партиционирования, которую никто не проверяет: найти старые партиции, удалить, запускать каждую ночь.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-why-application-lifecycle-should-not-belong-to-fastapi">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-why-application-lifecycle-should-not-belong-to-fastapi/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Почему жизненный цикл приложения не должен принадлежать FastAPI</h3>
        <p class="bdr-entry__description">lifespan FastAPI — хороший API: асинхронный контекстный менеджер с запуском до yield и остановкой после. Обычно туда помещают пул БД, прогрев, проверки здоровья и клиенты.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
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
  <article class="bdr-entry" data-article-id="2026-09-07-ai-code-review-should-not-be-fully-autonomous">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-ai-code-review-should-not-be-fully-autonomous/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Инструменты</div>
        <h3 class="bdr-entry__title">Почему ревью кода с ИИ не должно быть полностью автономным</h3>
        <p class="bdr-entry__description">Самый очевидный способ сделать ИИ-ревьюера — webhook: появляется merge request, модель читает diff, публикуются комментарии.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-why-i-stopped-wrapping-http-clients">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-why-i-stopped-wrapping-http-clients/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Почему я перестал писать обёртки над HTTP-клиентами</h3>
        <p class="bdr-entry__description">В каждой компании, где я работал, появлялась своя HTTP-обёртка: помощник повторов, класс конфигурации, метрики, затем class HttpClient в общем пакете, от которого зависят все и с…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-redis-health-checks-ping-is-not-the-whole-story">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-redis-health-checks-ping-is-not-the-whole-story/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Проверка здоровья Redis: одного PING недостаточно</h3>
        <p class="bdr-entry__description">Проверка, возвращающая True для сервера, неспособного принять запись, хуже отсутствующей: по её ответу принимают решения.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-the-production-checklist-for-aiokafka">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-the-production-checklist-for-aiokafka/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Проверки aiokafka перед выходом в продакшен</h3>
        <p class="bdr-entry__description">Aiokafka — хороший клиент со значениями по умолчанию для библиотеки, а не конкретного сервиса. В разнице между ними возникают инциденты.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-warmup-readiness-and-liveness-are-three-different-things">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-warmup-readiness-and-liveness-are-three-different-things/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Прогрев, readiness и liveness — три разные задачи</h3>
        <p class="bdr-entry__description">Большинство сервисов отвечает на все три вопроса одним обработчиком, обычно ping базы. Каждое смешение создаёт свой сбой.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-publishing-to-pypi-without-api-tokens">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-publishing-to-pypi-without-api-tokens/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Публикация в PyPI без API-токенов: полный путь Trusted Publishing</h3>
        <p class="bdr-entry__description">API-токен PyPI в секретах репозитория — пароль без срока действия, ограниченный проектом, но не объясняющий, кто именно его использовал.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-grpc-channels-pooled-by-identity">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-grpc-channels-pooled-by-identity/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Пул gRPC-каналов нельзя строить только по адресу</h3>
        <p class="bdr-entry__description">gRPC-канал дорого открывать и дёшево держать открытым. Поэтому у каждого сервиса с несколькими gRPC-зависимостями появляется пул каналов, а первый пул — всегда словарь с ключом…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-five-alembic-migration-tests">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-five-alembic-migration-tests/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Пять тестов миграций, которые стоит запускать в CI каждого Python-проекта</h3>
        <p class="bdr-entry__description">Мы тестируем приложение до зелёного значка покрытия, а затем развёртываем миграции БД, запущенные ровно один раз на ноутбуке в одну сторону.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>8 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-testing-migrations-with-testcontainers">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-testing-migrations-with-testcontainers/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Тестирование миграций с Testcontainers: вперёд, назад и снова вперёд</h3>
        <p class="bdr-entry__description">Статья о пяти тестах миграций объяснила, зачем они нужны. Здесь пошаговая настройка: от пустого tests/ до зелёной задачи CI, проходящей каждую ревизию вперёд, назад и снова…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>3 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-transactional-inbox">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-transactional-inbox/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Транзакционный inbox: вторая половина паттерна outbox</h3>
        <p class="bdr-entry__description">Outbox заметнее, потому что решает драматичную проблему: событие не ушло. Inbox решает тихую: событие пришло дважды либо consumer погиб посреди обработки.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-the-anatomy-of-a-production-grpc-server">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-the-anatomy-of-a-production-grpc-server/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Устройство gRPC-сервера на Python для продакшена</h3>
        <p class="bdr-entry__description">grpc.aio-сервер занимает шесть строк. Сервер, который можно поставить за балансировщиком, обновлять трижды в день и передать дежурной команде, требует набора решений, за каждым…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-what-every-microservice-reimplements">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-what-every-microservice-reimplements/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Что каждый Python-микросервис заново реализует для продакшена</h3>
        <p class="bdr-entry__description">Откройте репозиторий backend-сервиса, прожившего год в production, и найдите код, не относящийся к продукту.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-what-to-monitor-in-a-sqlalchemy-connection-pool/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Что отслеживать в пуле соединений SQLAlchemy</h3>
        <p class="bdr-entry__description">Первым обычно рисуют число занятых соединений, хотя оно мало говорит о качестве обслуживания. Я запустил восемь worker с пулом из четырёх, затем замедлил БД и посмотрел метрики.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-07-what-happens-when-kafka-is-down-for-an-hour">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-07-what-happens-when-kafka-is-down-for-an-hour/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Что происходит, когда Kafka недоступна целый час?</h3>
        <p class="bdr-entry__description">Не секунда сбоя, которую скрывает повтор, а час: неудачное обновление брокеров, заполненные диски, сетевое разделение зон.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-07">7 сент. 2026</time><span>·</span><span>4 мин на чтение</span></div>
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
        <p class="bdr-entry__description">Во всех сервисах, которые я запускал, на каждом исходящем вызове стоял таймаут. И каждый из этих сервисов всё равно умудрялся отвечать дольше любого числа в конфигурации.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-06">6 сент. 2026</time><span>·</span><span>9 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-06-pg-partsmith">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-06-pg-partsmith/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Библиотеки</div>
        <h3 class="bdr-entry__title">Управление партициями PostgreSQL: от одного сбоя к другому</h3>
        <p class="bdr-entry__description">Партиционированная таблица может поднять вас с постели двумя способами. Первый — INSERT в 03:00, который PostgreSQL отклоняет, потому что никто не создал партицию на следующий…</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-06">6 сент. 2026</time><span>·</span><span>10 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-05-30-welcome">
    <a class="bdr-entry__link bdr-card" href="posts/2026-05-30-welcome/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Добро пожаловать в блог Bedrock Python</h3>
        <p class="bdr-entry__description">Здесь мы рассказываем об экосистеме Bedrock Python: что это такое, зачем она существует и какие идеи за ней стоят.</p>
        <div class="bdr-entry__meta"><time datetime="2026-05-30">30 мая 2026</time><span>·</span><span>2 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-05-28-introducing-mr-review">
    <a class="bdr-entry__link bdr-card" href="posts/2026-05-28-introducing-mr-review/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Инструменты</div>
        <h3 class="bdr-entry__title">Знакомьтесь: mr-review — проверка merge request с помощью ИИ</h3>
        <p class="bdr-entry__description">Ревью кода — одна из самых полезных практик в разработке, но её качество сильно колеблется. Ревьюеры устают, переключаются между задачами прямо во время проверки и что-то упускают.</p>
        <div class="bdr-entry__meta"><time datetime="2026-05-28">28 мая 2026</time><span>·</span><span>2 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-05-15-transactional-outbox-with-omni-box">
    <a class="bdr-entry__link bdr-card" href="posts/2026-05-15-transactional-outbox-with-omni-box/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Библиотеки</div>
        <h3 class="bdr-entry__title">Паттерн Transactional Outbox на Python: omni-box</h3>
        <p class="bdr-entry__description">У распределённых систем есть классическая проблема: нужно обновить базу данных и опубликовать событие в Kafka в рамках одной операции, но общей транзакции между ними нет.</p>
        <div class="bdr-entry__meta"><time datetime="2026-05-15">15 мая 2026</time><span>·</span><span>2 мин на чтение</span></div>
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
