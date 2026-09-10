---
title: Bedrock Python
description: Библиотеки Python и инструменты разработчика для инфраструктуры современных бэкенд-сервисов.
hide:
  - navigation
  - toc
---

# Bedrock Python

<style>
  /* Landing page — hide the page H1 (we render our own hero) and the edit button. */
  .md-content__button { display: none !important; }
  .md-content__inner > h1:first-of-type { display: none; }
  .md-main__inner { margin-top: 0; }
</style>

<section class="bdr-home-hero" aria-labelledby="home-title" markdown="0">
  <div class="bdr-home-hero__copy">
    <div class="bdr-home-hero__eyebrow"><span></span> Экосистема Bedrock Python</div>
    <h1 id="home-title">Основа для<br>надёжных <em>Python</em><br>сервисов.</h1>
    <p class="bdr-home-hero__lede">Открытые библиотеки для инфраструктуры вашего сервиса. Жизненный цикл, клиенты, данные и отказоустойчивость — для единого производственного стека.</p>
    <div class="bdr-home-hero__actions">
      <a class="bdr-btn bdr-btn--primary" href="libraries/">Выбрать библиотеки <span aria-hidden="true">↗</span></a>
      <a class="bdr-home-hero__blog" href="blog/">Читать инженерный блог <span aria-hidden="true">→</span></a>
    </div>
    <div class="bdr-home-hero__proof">
      <a href="libraries/"><strong>12</strong> библиотек</a><span aria-hidden="true">/</span>
      <a href="tools/"><strong>2</strong> инструмента</a><span aria-hidden="true">/</span>
      <span>Открытый код</span>
    </div>
  </div>
  <figure class="bdr-stack" aria-labelledby="stack-caption">
    <div class="bdr-stack__heading"><span class="bdr-stack__index">01 — 04</span><span>Независимые части. Общая основа.</span></div>
    <!-- SVG links use xlink so instant navigation leaves their read-only href properties intact. -->
    <svg class="bdr-stack__diagram" viewBox="0 0 600 470" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-label="Четыре группы библиотек Bedrock Python">
      <defs>
        <pattern id="bdr-stack-dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="currentColor"/></pattern>
        <radialGradient id="bdr-stack-fade"><stop offset="0" stop-color="white"/><stop offset="1" stop-color="black"/></radialGradient>
        <mask id="bdr-stack-mask"><rect width="600" height="470" fill="url(#bdr-stack-fade)"/></mask>
      </defs>
      <g aria-hidden="true">
        <rect class="bdr-stack__dots" width="600" height="470" fill="url(#bdr-stack-dots)" mask="url(#bdr-stack-mask)"/>
        <path class="bdr-stack__floor" d="m46 354 170-85 170 85-170 85-170-85Zm34 17 170-85m-136 102 170-85m-136 102 170-85m-136 102 170-85M80 337l170 85M114 320l170 85M148 303l170 85M182 286l170 85"/>
        <path class="bdr-stack__axis" d="M216 42v383M76 137v217M356 137v217"/>
        <text class="bdr-stack__service-label" x="216" y="30" text-anchor="middle">ВАШ СЕРВИС НА PYTHON</text>
        <path class="bdr-stack__service-line" d="M216 40v23"/>
      </g>
      <a class="bdr-stack__layer bdr-stack__layer--database" xlink:href="libraries/#database" aria-label="Работа с БД: секции и тесты миграций">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 318 140 70v19L76 337Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 388 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 248 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 264 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__surface-detail" d="m132 306 84 42 84-42m-168 12 84 42 84-42"/>
        </g>
        <path class="bdr-stack__connector" d="M356 325h30l12 12h16"/>
        <circle class="bdr-stack__port" cx="356" cy="325" r="3"/>
        <text class="bdr-stack__number" x="420" y="319">04 / ЭКСПЛУАТАЦИЯ</text>
        <text class="bdr-stack__label" x="420" y="342">Работа с БД</text>
        <text class="bdr-stack__description" x="420" y="362">Секции · миграции</text>
        <path class="bdr-stack__link-arrow" d="M565 319h8v8m-8 0 8-8"/>
      </a>
      <a class="bdr-stack__layer bdr-stack__layer--reliability" xlink:href="libraries/#reliability" aria-label="Отказоустойчивость: Outbox, идемпотентность и дедлайны">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 257 140 70v19L76 276Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 327 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 187 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 203 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__surface-detail" d="m167 266 22 11 20-25 22 11 34-10"/>
        </g>
        <path class="bdr-stack__connector" d="M356 264h58"/>
        <circle class="bdr-stack__port" cx="356" cy="264" r="3"/>
        <text class="bdr-stack__number" x="420" y="246">03 / ЗАЩИТА</text>
        <text class="bdr-stack__label" x="420" y="269">Отказоустойчивость</text>
        <text class="bdr-stack__description" x="420" y="289">Outbox · ключи · дедлайны</text>
        <path class="bdr-stack__link-arrow" d="M565 246h8v8m-8 0 8-8"/>
      </a>
      <a class="bdr-stack__layer bdr-stack__layer--data" xlink:href="libraries/#data" aria-label="Данные и сообщения: PostgreSQL, Redis и Kafka">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 196 140 70v19L76 215Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 266 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 126 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 142 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__surface-detail" d="m158 202 20-10 20 10-20 10-20-10Zm39 20 20-10 20 10-20 10-20-10Zm40-20 20-10 20 10-20 10-20-10Z"/>
        </g>
        <path class="bdr-stack__connector" d="M356 203h30l12-12h16"/>
        <circle class="bdr-stack__port" cx="356" cy="203" r="3"/>
        <text class="bdr-stack__number" x="420" y="173">02 / ДАННЫЕ</text>
        <text class="bdr-stack__label" x="420" y="196">Данные и сообщения</text>
        <text class="bdr-stack__description" x="420" y="216">Postgres · Redis · Kafka</text>
        <path class="bdr-stack__link-arrow" d="M565 173h8v8m-8 0 8-8"/>
      </a>
      <a class="bdr-stack__layer bdr-stack__layer--runtime" xlink:href="libraries/#runtime" aria-label="Жизненный цикл и протоколы: сервисы, HTTP и gRPC">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 135 140 70v19L76 154Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 205 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 65 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 81 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__core-top" d="m216 98 42 21-42 21-42-21Z"/>
          <path class="bdr-stack__core-left" d="m174 119 42 21v33l-42-21Z"/>
          <path class="bdr-stack__core-right" d="m216 140 42-21v33l-42 21Z"/>
          <path class="bdr-stack__core-mark" d="m190 137 12 6m26 3 15-7"/>
        </g>
        <path class="bdr-stack__connector" d="M356 142h30l12-24h16"/>
        <circle class="bdr-stack__port" cx="356" cy="142" r="3"/>
        <text class="bdr-stack__number" x="420" y="100">01 / ЗАПУСК</text>
        <text class="bdr-stack__label" x="420" y="123">Сервисы и протоколы</text>
        <text class="bdr-stack__description" x="420" y="143">Сервисы · HTTP · gRPC</text>
        <path class="bdr-stack__link-arrow" d="M565 100h8v8m-8 0 8-8"/>
      </a>
      <g class="bdr-stack__base-note" aria-hidden="true"><path d="M192 434h48"/><text x="216" y="455" text-anchor="middle">НА ОСНОВЕ BEDROCK</text></g>
    </svg>
    <nav class="bdr-stack__mobile" aria-label="Компоненты инфраструктуры сервиса">
      <a href="libraries/#runtime"><span class="bdr-stack__mobile-number" data-layer="runtime">01</span><span><strong>Сервисы и протоколы</strong><small>Сервисы · HTTP · gRPC</small></span><span aria-hidden="true">↗</span></a>
      <a href="libraries/#data"><span class="bdr-stack__mobile-number" data-layer="data">02</span><span><strong>Данные и сообщения</strong><small>Postgres · Redis · Kafka</small></span><span aria-hidden="true">↗</span></a>
      <a href="libraries/#reliability"><span class="bdr-stack__mobile-number" data-layer="reliability">03</span><span><strong>Отказоустойчивость</strong><small>Outbox · ключи · дедлайны</small></span><span aria-hidden="true">↗</span></a>
      <a href="libraries/#database"><span class="bdr-stack__mobile-number" data-layer="database">04</span><span><strong>Работа с БД</strong><small>Секции · миграции</small></span><span aria-hidden="true">↗</span></a>
    </nav>
    <figcaption id="stack-caption"><span class="bdr-stack__caption-dot" aria-hidden="true"></span>Выберите слой инфраструктуры<span class="bdr-stack__caption-end" aria-hidden="true">↗</span></figcaption>
  </figure>
</section>

<section markdown="0">
<div class="bdr-section-head"><h2 class="bdr-section-head__title">Новое в блоге</h2><a class="bdr-section-head__link" href="blog/">Все статьи →</a></div>
<div class="bdr-grid">
<!-- catalog:home:start -->
<a class="bdr-card" href="blog/posts/2026-09-07-circuit-breakers-should-be-per-origin/">
  <div class="bdr-card__visual" aria-hidden="true"></div>
  <div class="bdr-card__eyebrow">Архитектура</div>
  <h3 class="bdr-card__title">Circuit breaker должен быть отдельным для каждого origin, а не клиента</h3>
  <p class="bdr-card__lede">Circuit breaker проще всего объяснить и проще всего привязать не к тому ключу. Объяснение помещается в предложение: после достаточного числа сбоев ненадолго прекратить вызовы…</p>
  <div class="bdr-card__meta">2026-09-07</div>
</a>
<a class="bdr-card" href="blog/posts/2026-09-07-pgbouncer-transaction-mode-async-sqlalchemy/">
  <div class="bdr-card__visual" aria-hidden="true"></div>
  <div class="bdr-card__eyebrow">Руководства</div>
  <h3 class="bdr-card__title">PgBouncer в режиме транзакций и асинхронный SQLAlchemy: рабочая конфигурация, которой не хватает в документации</h3>
  <p class="bdr-card__lede">Конфигурация SQLAlchemy прекрасно работает напрямую с PostgreSQL. Затем перед БД ставят PgBouncer в режиме транзакций, ради которого обычно и нужен пулер, и прежние предположения…</p>
  <div class="bdr-card__meta">2026-09-07</div>
</a>
<a class="bdr-card" href="blog/posts/2026-09-07-retry-after-backoff-and-jitter/">
  <div class="bdr-card__visual" aria-hidden="true"></div>
  <div class="bdr-card__eyebrow">Руководства</div>
  <h3 class="bdr-card__title">Retry-After, backoff и jitter: что делает HTTP-клиент в продакшене</h3>
  <p class="bdr-card__lede">Обычный цикл повторов — четыре строки: попытаться, поймать, подождать, повторить. Рабочая политика HTTP-клиента требует примерно восьми решений, которые этот цикл молча принимает…</p>
  <div class="bdr-card__meta">2026-09-07</div>
</a>
<!-- catalog:home:end -->
</div>
</section>

<section class="bdr-home-pathways" aria-labelledby="home-pathways-title" markdown="0">
  <div class="bdr-home-pathways__heading">
    <div>
      <div class="bdr-home-pathways__eyebrow">ОТ ИДЕЙ К ПРАКТИКЕ</div>
      <h2 id="home-pathways-title">Примените знания в деле.</h2>
    </div>
    <p>Выберите задачу и найдите, с чего начать.</p>
  </div>
  <div class="bdr-home-pathways__grid">
    <article class="bdr-home-path bdr-home-path--libraries" aria-labelledby="home-libraries-title">
      <div class="bdr-home-path__intro">
        <div class="bdr-home-path__heading">
          <div>
            <span class="bdr-home-path__label">01 / БИБЛИОТЕКИ</span>
            <h3 id="home-libraries-title">Создайте свой сервис.</h3>
          </div>
          <span class="bdr-home-path__icon" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><path d="m16 4 11 6-11 6-11-6 11-6Zm-11 6v12l11 6 11-6V10M16 16v12M5 16l11 6 11-6"/></svg></span>
        </div>
        <p>Библиотеки Python для жизненного цикла сервиса, работы с данными и отказоустойчивости.</p>
      </div>
      <nav class="bdr-home-path__routes" aria-label="Выбрать библиотеку по задаче">
        <a href="libraries/#runtime"><span>Запустить сервис на Python</span><small>Сервисы · HTTP · gRPC</small><span aria-hidden="true">↗</span></a>
        <a href="libraries/#data"><span>Подключить хранилища</span><small>Postgres · Redis · Kafka</small><span aria-hidden="true">↗</span></a>
        <a href="libraries/#reliability"><span>Повысить надёжность</span><small>Outbox · ключи · дедлайны</small><span aria-hidden="true">↗</span></a>
      </nav>
      <a class="bdr-home-path__all" href="libraries/">Все библиотеки <span aria-hidden="true">→</span></a>
    </article>
    <article class="bdr-home-path bdr-home-path--tools" aria-labelledby="home-tools-title">
      <div class="bdr-home-path__intro">
        <div class="bdr-home-path__heading">
          <div>
            <span class="bdr-home-path__label">02 / ИНСТРУМЕНТЫ</span>
            <h3 id="home-tools-title">Избавьтесь от рутины.</h3>
          </div>
          <span class="bdr-home-path__icon" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><rect x="4" y="6" width="24" height="20" rx="3"/><path d="M4 12h24m-17 5 3 3-3 3m7 0h5"/><path d="M8 9h.01M11 9h.01"/></svg></span>
        </div>
        <p>Инструменты для ревью кода, поиска ответов и планирования изменений в базе данных.</p>
      </div>
      <nav class="bdr-home-path__routes" aria-label="Выбрать инструмент по задаче">
        <a href="tools/#mr-review"><span>Проверить код</span><small>mr-review</small><span aria-hidden="true">↗</span></a>
        <a href="tools/#mattermind"><span>Найти ответ в переписке</span><small>mattermind</small><span aria-hidden="true">↗</span></a>
        <a href="tools/#from-libraries"><span>Спланировать изменения в БД</span><small>pg-partsmith CLI</small><span aria-hidden="true">↗</span></a>
      </nav>
      <a class="bdr-home-path__all" href="tools/">Все инструменты <span aria-hidden="true">→</span></a>
    </article>
  </div>
</section>
