---
title: Библиотеки
description: Библиотеки Python для жизненного цикла сервисов, работы с данными и отказоустойчивости. Компактный каталог с поиском и командами установки.
hide:
  - navigation
  - toc
---

<div class="bdr-catalog bdr-library-page" data-library-page markdown="0">
  <header class="bdr-lib-hero">
    <div class="bdr-lib-hero__copy">
      <div class="bdr-lib-eyebrow"><span></span> СТРОИТЕЛЬНЫЕ БЛОКИ / БИБЛИОТЕКИ</div>
      <h1>Небольшие части.<br><em>Надёжная основа.</em></h1>
      <p>Двенадцать библиотек Python для инфраструктуры вашего сервиса. Выбирайте нужное: общие принципы позволяют частям работать вместе.</p>
      <div class="bdr-lib-principles"><span>Строгая типизация</span><span>Опциональные зависимости</span><span>Apache 2.0</span></div>
      <a class="bdr-lib-hero__link" href="#library-directory">Выбрать компоненты <span aria-hidden="true">↓</span></a>
    </div>
    <div class="bdr-lib-composer" aria-label="Пример стека из независимых пакетов Python">
      <div class="bdr-lib-composer__header"><span>СОБЕРИТЕ СВОЙ СТЕК</span><span aria-hidden="true">⌘</span></div>
      <div class="bdr-lib-composer__packages">
        <a class="bdr-lib-piece bdr-lib-piece--runtime" href="#package-servicewright"><span class="bdr-lib-piece__icon" aria-hidden="true">◷</span><div><span>ЖИЗНЕННЫЙ ЦИКЛ</span><strong>servicewright</strong></div><span class="bdr-lib-piece__arrow" aria-hidden="true">↗</span></a>
        <div class="bdr-lib-composer__connector" aria-hidden="true">+</div>
        <a class="bdr-lib-piece bdr-lib-piece--data" href="#package-sqlalchemy-foundation-kit"><span class="bdr-lib-piece__icon" aria-hidden="true">▤</span><div><span>СЛОЙ ДАННЫХ</span><strong>sqlalchemy-foundation-kit</strong></div><span class="bdr-lib-piece__arrow" aria-hidden="true">↗</span></a>
        <div class="bdr-lib-composer__connector" aria-hidden="true">+</div>
        <a class="bdr-lib-piece bdr-lib-piece--reliability" href="#package-omni-box"><span class="bdr-lib-piece__icon" aria-hidden="true">⇢</span><div><span>ГАРАНТИИ ДОСТАВКИ</span><strong>omni-box</strong></div><span class="bdr-lib-piece__arrow" aria-hidden="true">↗</span></a>
      </div>
      <div class="bdr-lib-composer__footer"><span aria-hidden="true">↳</span> Независимые пакеты. Общий инженерный стандарт.</div>
    </div>
  </header>

  <nav class="bdr-lib-layers" aria-label="Категории библиотек">
    <a href="#runtime" class="bdr-lib-layer" data-layer="runtime"><span class="bdr-lib-layer__top"><span>01 / ЗАПУСК</span><span>4 библиотеки</span></span><strong>Сервисы и протоколы <span aria-hidden="true">↗</span></strong><span>Сервисы, HTTP и gRPC</span></a>
    <a href="#data" class="bdr-lib-layer" data-layer="data"><span class="bdr-lib-layer__top"><span>02 / ДАННЫЕ</span><span>3 библиотеки</span></span><strong>Данные и сообщения <span aria-hidden="true">↗</span></strong><span>Postgres, Redis и Kafka</span></a>
    <a href="#reliability" class="bdr-lib-layer" data-layer="reliability"><span class="bdr-lib-layer__top"><span>03 / ЗАЩИТА</span><span>3 библиотеки</span></span><strong>Отказоустойчивость <span aria-hidden="true">↗</span></strong><span>Outbox, идемпотентность и дедлайны</span></a>
    <a href="#database" class="bdr-lib-layer" data-layer="database"><span class="bdr-lib-layer__top"><span>04 / ЭКСПЛУАТАЦИЯ</span><span>2 библиотеки</span></span><strong>Работа с БД <span aria-hidden="true">↗</span></strong><span>Секции и тесты миграций</span></a>
  </nav>

  <section class="bdr-lib-directory" id="library-directory" aria-label="Каталог пакетов">
    <div class="bdr-lib-directory__heading"><h2>Каталог пакетов</h2><span>12 библиотек Bedrock и полезные проекты сообщества</span></div>
    <div class="bdr-lib-toolbar">
      <div class="bdr-lib-search" role="search" aria-label="Найти библиотеку" data-library-controls hidden><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><label class="bdr-lib-sr-only" for="library-query">Поиск по пакетам, возможностям и технологиям</label><input id="library-query" data-library-query type="search" placeholder="Пакет, возможность, технология…" autocomplete="off" enterkeyhint="search"><button type="button" data-library-clear aria-label="Очистить поиск пакетов" hidden>×</button></div>
      <nav class="bdr-lib-extras" aria-label="Дополнительные ресурсы"><a href="#template">Создать библиотеку ↗</a><a href="#recommended">Проекты сообщества ↗</a></nav>
    </div>
    <p class="bdr-lib-status" data-library-status role="status" aria-live="polite" hidden></p>

    <section class="bdr-lib-group" id="runtime" data-library-group data-layer="runtime" aria-labelledby="library-runtime-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">01</span><h2 id="library-runtime-title">Жизненный цикл и протоколы</h2><span class="bdr-lib-group__count">4</span></div><p>Запускайте сервисы и связывайте их между собой.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-servicewright" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="servicewright" href="https://pypi.org/project/servicewright/" title="servicewright на PyPI">v0.9.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/servicewright/">servicewright<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Один <code>Host</code> и несколько <code>Entrypoint</code>: FastAPI, Litestar, gRPC, планировщик, демон или разовая задача с единым жизненным циклом, корректным для Kubernetes.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>ядро без зависимостей</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/servicewright/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/servicewright">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add servicewright</code><button type="button" data-copy-command="uv add servicewright" aria-label="Скопировать команду установки servicewright" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-clientwright" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="clientwright" href="https://pypi.org/project/clientwright/" title="clientwright на PyPI">v0.2.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/clientwright/">clientwright<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Общее ядро отказоустойчивости и наблюдаемости <em>под</em> публичным API httpx, aiohttp, requests и urllib3 — вы получаете привычный клиент выбранной библиотеки.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>ядро без зависимостей</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/clientwright/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/clientwright">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add clientwright</code><button type="button" data-copy-command="uv add clientwright" aria-label="Скопировать команду установки clientwright" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-grpc-server-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="grpc-server-kit" href="https://pypi.org/project/grpc-server-kit/" title="grpc-server-kit на PyPI">v0.1.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/grpc-server-kit/">grpc-server-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Серверы <code>grpc.aio</code> без шаблонного кода: фасад <code>GrpcApp</code>, TLS/mTLS, корректное завершение, проверки состояния и перехватчики с поддержкой потоковых вызовов.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>только grpcio</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/grpc-server-kit/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/grpc-server-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add grpc-server-kit</code><button type="button" data-copy-command="uv add grpc-server-kit" aria-label="Скопировать команду установки grpc-server-kit" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-grpc-client-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v4m0 10v4M3 12h4m10 0h4"/><rect x="7" y="7" width="10" height="10" rx="2"/></svg></span>
            <a class="bdr-package__version" data-pypi="grpc-client-kit" href="https://pypi.org/project/grpc-client-kit/" title="grpc-client-kit на PyPI">v0.1.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/grpc-client-kit/">grpc-client-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Клиентская сторона: пул каналов с учётом всех параметров, балансировка нагрузки, мониторинг состояния и повторы в рамках общего дедлайна вызова.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>только grpcio</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/grpc-client-kit/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/grpc-client-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add grpc-client-kit</code><button type="button" data-copy-command="uv add grpc-client-kit" aria-label="Скопировать команду установки grpc-client-kit" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="data" data-library-group data-layer="data" aria-labelledby="library-data-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">02</span><h2 id="library-data-title">Данные и обмен сообщениями</h2><span class="bdr-lib-group__count">3</span></div><p>Postgres, Redis, Kafka — клиенты для повседневных задач сервиса.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-sqlalchemy-foundation-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg></span>
            <a class="bdr-package__version" data-pypi="sqlalchemy-foundation-kit" href="https://pypi.org/project/sqlalchemy-foundation-kit/" title="sqlalchemy-foundation-kit на PyPI">v0.2.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">sqlalchemy-foundation-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Асинхронные сессии, совместимые с PgBouncer, Unit of Work, базовые ORM-модели, метрики пула, трассировка и провайдеры для dishka и dependency-injector.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/sqlalchemy-foundation-kit/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/sqlalchemy-foundation-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add sqlalchemy-foundation-kit</code><button type="button" data-copy-command="uv add sqlalchemy-foundation-kit" aria-label="Скопировать команду установки sqlalchemy-foundation-kit" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-redis-client-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg></span>
            <a class="bdr-package__version" data-pypi="redis-client-kit" href="https://pypi.org/project/redis-client-kit/" title="redis-client-kit на PyPI">v0.1.2</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/redis-client-kit/">redis-client-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Асинхронные и синхронные клиенты redis-py: кластеры, пул соединений, проверки состояния и повторы. Настройки Pydantic, Prometheus и Dishka подключаются отдельно.</p>
          <div class="bdr-package__tags"><span>Python 3.10+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/redis-client-kit/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/redis-client-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add redis-client-kit</code><button type="button" data-copy-command="uv add redis-client-kit" aria-label="Скопировать команду установки redis-client-kit" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-aiokafka-foundation-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/></svg></span>
            <a class="bdr-package__version" data-pypi="aiokafka-foundation-kit" href="https://pypi.org/project/aiokafka-foundation-kit/" title="aiokafka-foundation-kit на PyPI">v0.1.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/aiokafka-foundation-kit/">aiokafka-foundation-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Фабрики producer и consumer на aiokafka с настройками Pydantic, политиками повторов, проверками состояния, метриками Prometheus и OpenTelemetry.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/aiokafka-foundation-kit/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/aiokafka-foundation-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add aiokafka-foundation-kit</code><button type="button" data-copy-command="uv add aiokafka-foundation-kit" aria-label="Скопировать команду установки aiokafka-foundation-kit" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="reliability" data-library-group data-layer="reliability" aria-labelledby="library-reliability-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">03</span><h2 id="library-reliability-title">Отказоустойчивость</h2><span class="bdr-lib-group__count">3</span></div><p>Однократные эффекты и ограниченное время выполнения.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-omni-box" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></svg></span>
            <a class="bdr-package__version" data-pypi="omni-box" href="https://pypi.org/project/omni-box/" title="omni-box на PyPI">v0.1.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/omni-box/">omni-box<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Транзакционные Outbox и Inbox: событие сохраняется в одной транзакции с бизнес-данными, отправляется в Kafka фоновым процессом и принимается с дедупликацией.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/omni-box/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/omni-box">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add omni-box</code><button type="button" data-copy-command="uv add omni-box" aria-label="Скопировать команду установки omni-box" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-idempotency-kit" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></svg></span>
            <a class="bdr-package__version" data-pypi="idempotency-kit" href="https://pypi.org/project/idempotency-kit/" title="idempotency-kit на PyPI">v0.1.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/idempotency-kit/">idempotency-kit<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Одно выполнение операции на ключ идемпотентности: координатор и декоратор поверх Redis, обработка коллизий, управляемая деградация и метрики.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/idempotency-kit/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/idempotency-kit">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add idempotency-kit</code><button type="button" data-copy-command="uv add idempotency-kit" aria-label="Скопировать команду установки idempotency-kit" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-deadline-budget" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 8 3v6c0 4-4 7-8 9-4-2-8-5-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/></svg></span>
            <a class="bdr-package__version" data-pypi="deadline-budget" href="https://pypi.org/project/deadline-budget/" title="deadline-budget на PyPI">v0.1.2</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/deadline-budget/">deadline-budget<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Общий бюджет времени запроса с ограничением на каждый вызов и запасом на завершение. Его передают между сервисами clientwright, grpc-client-kit и servicewright.</p>
          <div class="bdr-package__tags"><span>Python 3.10+</span><span>без зависимостей</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/deadline-budget/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/deadline-budget">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add deadline-budget</code><button type="button" data-copy-command="uv add deadline-budget" aria-label="Скопировать команду установки deadline-budget" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="database" data-library-group data-layer="database" aria-labelledby="library-database-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">04</span><h2 id="library-database-title">Эксплуатация и тестирование БД</h2><span class="bdr-lib-group__count">2</span></div><p>Планируйте секции. Проверяйте миграции.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-pg-partsmith" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16m-9 0v10"/></svg></span>
            <a class="bdr-package__version" data-pypi="pg-partsmith" href="https://pypi.org/project/pg-partsmith/" title="pg-partsmith на PyPI">v1.5.0</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/pg-partsmith/">pg-partsmith<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Управление секциями PostgreSQL с просмотром плана до выполнения. RANGE, LIST и HASH с любой глубиной вложенности — библиотека, CLI и контейнер.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span><span>стабильная версия</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/pg-partsmith/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/pg-partsmith">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add pg-partsmith</code><button type="button" data-copy-command="uv add pg-partsmith" aria-label="Скопировать команду установки pg-partsmith" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-alembic-gauntlet" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 10h16m-9 0v10"/></svg></span>
            <a class="bdr-package__version" data-pypi="alembic-gauntlet" href="https://pypi.org/project/alembic-gauntlet/" title="alembic-gauntlet на PyPI">v0.2.1</a>
          </div>
          <h3><a href="https://bedrock-python.github.io/alembic-gauntlet/">alembic-gauntlet<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Плагин pytest для проверки миграций Alembic: пошаговые upgrade и downgrade, расхождения моделей, единственная головная ревизия, полный откат и правила именования.</p>
          <div class="bdr-package__tags"><span>Python 3.10+</span><span>плагин pytest</span></div>
          <div class="bdr-package__links"><a href="https://bedrock-python.github.io/alembic-gauntlet/">Документация <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/bedrock-python/alembic-gauntlet">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add alembic-gauntlet</code><button type="button" data-copy-command="uv add alembic-gauntlet" aria-label="Скопировать команду установки alembic-gauntlet" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="template" data-library-group data-layer="template" aria-labelledby="library-template-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">05</span><h2 id="library-template-title">Создайте свою библиотеку</h2><span class="bdr-lib-group__count">1</span></div><p>Каждая из этих библиотек начиналась здесь.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-python-library-template" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-14-2 16"/></svg></span>
            <span class="bdr-package__kind">ШАБЛОН ПРОЕКТА</span>
          </div>
          <h3><a href="https://github.com/bedrock-python/python-library-template">python-library-template<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Шаблон Copier: uv, hatchling, ruff, mypy, модульные и интеграционные тесты pytest, документация Zensical, Release Please с доверенной публикацией на PyPI и общие настройки репозитория.</p>
          <div class="bdr-package__tags"><span>шаблон Copier</span></div>
          <div class="bdr-package__links"><a href="https://github.com/bedrock-python/python-library-template">Использовать шаблон <span aria-hidden="true">↗</span></a>
          </div>
        </article>
      </div>
    </section>
    <section class="bdr-lib-group" id="recommended" data-library-group data-layer="recommended" aria-labelledby="library-recommended-title">
      <div class="bdr-lib-group__heading"><div><span class="bdr-lib-group__number">06</span><h2 id="library-recommended-title">Рекомендуем</h2><span class="bdr-lib-group__count">2</span></div><p>Проекты сообщества с близким подходом к качеству.</p></div>
      <div class="bdr-lib-grid">
        <article class="bdr-package" id="package-aiofence" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 2.8 5.7L21 9.6l-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg></span>
            <a class="bdr-package__version" data-pypi="aiofence" href="https://pypi.org/project/aiofence/" title="aiofence на PyPI">v0.4.0</a>
          </div>
          <h3><a href="https://github.com/stanislaushimovolos/aiofence">aiofence<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Отмена asyncio-задач по нескольким причинам в духе <code>context.Context</code> из Go. Задайте таймаут, отключение клиента и завершение сервиса на границе запроса, передайте их через <code>ContextVar</code>, оберните нужную работу в <code>Fence</code> и узнайте причину отмены.</p>
          <div class="bdr-package__tags"><span>Python 3.12+</span><span>автор — Станислав Шимоволос</span></div>
          <div class="bdr-package__links"><a href="https://github.com/stanislaushimovolos/aiofence">Открыть проект <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/stanislaushimovolos/aiofence">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add aiofence</code><button type="button" data-copy-command="uv add aiofence" aria-label="Скопировать команду установки aiofence" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
        <article class="bdr-package" id="package-d9d" data-library-package>
          <div class="bdr-package__top"><span class="bdr-package__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="m12 3 2.8 5.7L21 9.6l-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg></span>
            <a class="bdr-package__version" data-pypi="d9d" href="https://pypi.org/project/d9d/" title="d9d на PyPI">v0.19.0</a>
          </div>
          <h3><a href="https://d9d-project.github.io/d9d/">d9d<span aria-hidden="true">↗</span></a></h3>
          <p class="bdr-package__description">Гибкий фреймворк распределённого обучения на PyTorch 2: комбинируемые стратегии параллелизма, обычные <code>nn.Module</code>, <code>DTensor</code> для распределённых параметров и граф контрольных точек — от отладки на одной GPU до кластеров с шестимерным параллелизмом.</p>
          <div class="bdr-package__tags"><span>Python 3.11+</span><span>Apache-2.0</span></div>
          <div class="bdr-package__links"><a href="https://d9d-project.github.io/d9d/">Открыть проект <span aria-hidden="true">↗</span></a>
            <a class="bdr-package__github" href="https://github.com/d9d-project/d9d">GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <div class="bdr-package__install"><code>uv add d9d</code><button type="button" data-copy-command="uv add d9d" aria-label="Скопировать команду установки d9d" title="Скопировать команду установки" hidden><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h2"/></svg></button></div>
        </article>
      </div>
    </section>
    <div class="bdr-lib-empty" data-library-empty hidden><h3>Пакеты не найдены.</h3><p>Попробуйте более общий запрос: «Kafka», «клиент» или «миграции».</p><button type="button" data-library-reset>Очистить поиск</button></div>
  </section>
  <p class="bdr-lib-footnote">Метки версий ведут на PyPI и обновляются при загрузке страницы.</p>
  <div class="bdr-lib-sr-only" data-library-copy-status role="status" aria-live="polite"></div>
</div>
