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
