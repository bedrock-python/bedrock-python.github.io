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
      <a class="bdr-collection bdr-collection--postgres" data-blog-collection="postgres" href="posts/2026-10-18-postgresql-partition-maintenance/">
        <div class="bdr-collection__icon" aria-hidden="true"><svg viewBox="0 0 48 48" fill="none"><ellipse cx="24" cy="11" rx="15" ry="6"/><path d="M9 11v25c0 3.3 6.7 6 15 6s15-2.7 15-6V11M9 23c0 3.3 6.7 6 15 6s15-2.7 15-6M9 35c0 3.3 6.7 6 15 6s15-2.7 15-6"/></svg></div>
        <div><span class="bdr-collection__label">ЗА ПРЕДЕЛАМИ ЗАПРОСА</span><h3>Postgres в эксплуатации</h3><p>Секции, сессии и миграции</p></div><span class="bdr-collection__arrow" aria-hidden="true">↗</span>
      </a>
      <a class="bdr-collection bdr-collection--messaging" data-blog-collection="messaging" href="posts/2026-10-03-reliable-events-outbox-inbox-kafka/">
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
  <article class="bdr-entry" data-article-id="2026-10-29-ai-code-review-should-not-be-fully-autonomous">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-29-ai-code-review-should-not-be-fully-autonomous/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Инструменты</div>
        <h3 class="bdr-entry__title">Почему замечания ИИ-ревью нужно проверять</h3>
        <p class="bdr-entry__description">Многие команды подключили к merge request ИИ-ревьюера. Он пишет замечания уверенно, как опытный коллега, но уверенный тон ещё не значит, что замечание верно.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-29">29 окт. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-27-why-bedrock-python-libraries">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-27-why-bedrock-python-libraries/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Зачем выделять инфраструктуру Python-сервисов в библиотеки</h3>
        <p class="bdr-entry__description">Когда сервисов становится больше одного, у них появляется общая обвязка: пул соединений, ретраи, дедлайн запроса, порядок остановки.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-27">27 окт. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-26-documentation-for-ai-coding-agents">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-26-documentation-for-ai-coding-agents/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Об экосистеме</div>
        <h3 class="bdr-entry__title">Документация, с которой ИИ-агент пишет проверяемый код</h3>
        <p class="bdr-entry__description">Всё больше кода в сервисах пишут ИИ-агенты, и пишут его по той документации, которая есть у проекта. Чего в ней не хватает, агент додумывает сам, и не всегда верно.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-26">26 окт. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-22-python-library-from-template-to-release">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-22-python-library-from-template-to-release/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Python-библиотека от шаблона до релиза</h3>
        <p class="bdr-entry__description">Небольшой общий код часто живёт копиями: в каждом сервисе своя функция, и со временем они расходятся.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-22">22 окт. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-21-zero-dependency-cores">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-21-zero-dependency-cores/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Python и инструменты <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Ядро без зависимостей: подключаем только нужные интеграции</h3>
        <p class="bdr-entry__description">Инфраструктурную библиотеку ставят во многие сервисы, и каждая её обязательная зависимость попадает в каждый из них, даже туда, где она не нужна.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-21">21 окт. 2026</time><span>·</span><span>5 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-18-postgresql-partition-maintenance">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-18-postgresql-partition-maintenance/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Обслуживание партиций PostgreSQL: от плана до проверенного архива</h3>
        <p class="bdr-entry__description">Месячные партиции требуют ухода: каждый месяц кто-то должен создать таблицу на следующий месяц и убрать старую.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-18">18 окт. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-17-partitioning-an-existing-postgresql-table">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-17-partitioning-an-existing-postgresql-table/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Как перевести таблицу PostgreSQL на партиционирование</h3>
        <p class="bdr-entry__description">Таблица событий растёт годами, и однажды запросы и удаление старых данных упираются в её размер. Тогда её решают разбить на месячные партиции.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-17">17 окт. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-11-testing-alembic-migrations-in-ci">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-11-testing-alembic-migrations-in-ci/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Как проверять миграции Alembic в CI</h3>
        <p class="bdr-entry__description">Миграции схемы обычно проверяют в CI одним шагом: накатывают их на пустую базу. Если шаг зелёный, миграцию считают безопасной.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-11">11 окт. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-09-sqlalchemy-pgbouncer-pools">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-09-sqlalchemy-pgbouncer-pools/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">SQLAlchemy и PgBouncer: настройка и диагностика пула соединений</h3>
        <p class="bdr-entry__description">Когда сервисов и подов становится много, соединений с PostgreSQL перестаёт хватать, и перед базой ставят PgBouncer.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-09">9 окт. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-08-sqlalchemy-sessions-and-transactions">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-08-sqlalchemy-sessions-and-transactions/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">PostgreSQL и SQLAlchemy <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Сессии и транзакции в SQLAlchemy: кто отвечает за commit</h3>
        <p class="bdr-entry__description">Представьте сервис заказов интернет-магазина. Покупатель оформляет заказ, сервис сохраняет его и пишет событие created, по которому о заказе узнают склад и доставка.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-08">8 окт. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-03-reliable-events-outbox-inbox-kafka">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-03-reliable-events-outbox-inbox-kafka/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Надёжная доставка событий: Outbox, Inbox и сбои Kafka</h3>
        <p class="bdr-entry__description">Представьте: покупатель оформляет заказ. Сервис заказов сохраняет его в PostgreSQL и публикует событие в Kafka. Биллинг читает это событие и выставляет счёт.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-03">3 окт. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-10-02-kafka-in-python-services">
    <a class="bdr-entry__link bdr-card" href="posts/2026-10-02-kafka-in-python-services/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Kafka и обмен сообщениями <span>·</span> Руководства</div>
        <h3 class="bdr-entry__title">Kafka в Python: отправка, обработка и остановка сервиса</h3>
        <p class="bdr-entry__description">Сервис доставки публикует статусы посылок в Kafka, а сервис отслеживания читает их и показывает покупателю, где сейчас заказ.</p>
        <div class="bdr-entry__meta"><time datetime="2026-10-02">2 окт. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-30-redis-failures-and-health-checks">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-30-redis-failures-and-health-checks/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Redis недоступен: какие запросы продолжают работать и почему PING об этом не скажет</h3>
        <p class="bdr-entry__description">В интернет-магазине Redis обычно стоит рядом с основной базой: кеширует цены, считает попытки входа и не пускает повторные нажатия «Оплатить». Пока он работает, о нём не думают.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-30">30 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-23-production-python-grpc-server">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-23-production-python-grpc-server/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Как подготовить gRPC-сервер на Python к продакшену</h3>
        <p class="bdr-entry__description">Поднять gRPC-сервер на Python несложно: хватает обработчика и пары строк запуска. Сложнее добиться, чтобы он вёл себя предсказуемо, когда что-то идёт не так.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-23">23 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-20-python-service-lifecycle">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-20-python-service-lifecycle/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Жизненный цикл сервиса <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Жизненный цикл Python-сервиса: запуск, проверки состояния и остановка</h3>
        <p class="bdr-entry__description">Сервис в Kubernetes перезапускают постоянно: при выкатке, масштабировании, переезде пода на другой узел.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-20">20 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-14-idempotency-in-apis-and-background-jobs">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-14-idempotency-in-apis-and-background-jobs/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">Redis и идемпотентность <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Идемпотентность в API и фоновых задачах</h3>
        <p class="bdr-entry__description">Сеть теряет ответы, пользователи нажимают кнопку второй раз, брокеры доставляют сообщения повторно. Поэтому любой запрос и любое задание однажды придут дважды.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-14">14 сент. 2026</time><span>·</span><span>5 мин на чтение</span></div>
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
        <p class="bdr-entry__description">Сервис заказов ходит на склад и в платёжный сервис, и любой из них иногда отвечает медленно или не отвечает вовсе. Первое, что хочется сделать, это повторить запрос.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-13">13 сент. 2026</time><span>·</span><span>7 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-08-why-grpc-interceptors-break-on-streaming-rpcs">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-08-why-grpc-interceptors-break-on-streaming-rpcs/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">gRPC <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Почему интерцепторы gRPC ломаются на потоковых RPC</h3>
        <p class="bdr-entry__description">Интерцепторы в gRPC обычно пишут один раз, чтобы логи, метрики и трассировка работали для всех вызовов сразу.</p>
        <div class="bdr-entry__meta"><time datetime="2026-09-08">8 сент. 2026</time><span>·</span><span>6 мин на чтение</span></div>
      </div>
      <div class="bdr-entry__visual bdr-card__visual" aria-hidden="true"></div>
      <span class="bdr-entry__arrow" aria-hidden="true">↗</span>
    </a>
  </article>
  <article class="bdr-entry" data-article-id="2026-09-06-timeouts-are-not-deadlines">
    <a class="bdr-entry__link bdr-card" href="posts/2026-09-06-timeouts-are-not-deadlines/">
      <div class="bdr-entry__body">
        <div class="bdr-entry__eyebrow">HTTP и отказоустойчивость <span>·</span> Архитектура</div>
        <h3 class="bdr-entry__title">Почему таймаут не заменяет дедлайн в микросервисах</h3>
        <p class="bdr-entry__description">Запрос пользователя редко обслуживает один сервис. Обычно он проходит цепочку вызовов, у каждого вызова свой таймаут, и кажется, что этого хватит, чтобы запрос не висел вечно.</p>
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
