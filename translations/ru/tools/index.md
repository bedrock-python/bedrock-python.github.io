---
title: Инструменты
description: Инструменты разработчика для ревью кода, поиска в рабочем пространстве и работы с PostgreSQL. На Python, для ваших задач.
hide:
  - navigation
  - toc
---

<div class="bdr-tools-page" markdown="0">
  <header class="bdr-tool-hero">
    <div class="bdr-tool-hero__copy">
      <div class="bdr-tool-eyebrow"><span></span> МАСТЕРСКАЯ / ИНСТРУМЕНТЫ РАЗРАБОТЧИКА</div>
      <h1>Меньше рутины.<br><em>Больше дела.</em></h1>
      <p>Проверьте изменения, найдите контекст, спланируйте следующий шаг. Инструменты на Python для задач вокруг вашего кода.</p>
      <div class="bdr-tool-hero__principles"><span>На вашем сервере</span><span>Открытый код</span><span>Для реальных задач</span></div>
    </div>
    <nav class="bdr-tool-jumps" aria-label="Выбрать инструмент для вашей задачи">
      <div class="bdr-tool-jumps__label">НАД ЧЕМ ВЫ РАБОТАЕТЕ?</div>
      <a href="#mr-review"><span class="bdr-tool-jumps__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M6 6v12m12-12v5a5 5 0 0 1-5 5H6"/><circle cx="6" cy="4" r="2"/><circle cx="6" cy="20" r="2"/><circle cx="18" cy="4" r="2"/></svg></span><span><strong>Проверить изменения</strong><small>mr-review</small></span><span aria-hidden="true">↗</span></a>
      <a href="#mattermind"><span class="bdr-tool-jumps__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M20 14a3 3 0 0 1-3 3H9l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v8Z"/><path d="M8 8h8m-8 4h5"/></svg></span><span><strong>Найти ответ</strong><small>mattermind</small></span><span aria-hidden="true">↗</span></a>
      <a href="#from-libraries"><span class="bdr-tool-jumps__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3m6 0h4"/></svg></span><span><strong>Спланировать изменения в БД</strong><small>pg-partsmith CLI</small></span><span aria-hidden="true">↗</span></a>
    </nav>
  </header>

  <section class="bdr-tool-section" id="standalone" aria-labelledby="standalone-title">
    <div class="bdr-tool-section__heading"><div><span>01 / САМОСТОЯТЕЛЬНЫЕ ИНСТРУМЕНТЫ</span><h2 id="standalone-title">Готовы к вашей работе.</h2></div><p>Установите, подключите и приступайте.</p></div>
    <div class="bdr-tool-grid">
      <article class="bdr-tool-card bdr-tool-card--review" id="mr-review">
        <div class="bdr-tool-art bdr-tool-art--review" aria-hidden="true">
          <div class="bdr-tool-art__label"><span>ОСМЫСЛЕННОЕ РЕВЬЮ КОДА</span><span>01</span></div>
          <svg class="bdr-tool-review-drawing" viewBox="0 0 480 220" fill="none">
            <path class="bdr-tool-art__guide" d="M40 175h400M105 25v165M375 25v165"/>
            <rect class="bdr-tool-art__paper" x="67" y="28" width="180" height="145" rx="8"/>
            <path class="bdr-tool-art__rule" d="M67 56h180"/>
            <circle class="bdr-tool-art__dot" cx="83" cy="42" r="3"/><circle class="bdr-tool-art__dot" cx="95" cy="42" r="3"/><circle class="bdr-tool-art__dot" cx="107" cy="42" r="3"/>
            <path class="bdr-tool-art__code" d="M85 78h18m13 0h77M85 98h18m13 0h95M85 118h18m13 0h50M85 138h18m13 0h69"/>
            <path class="bdr-tool-art__accent-line" d="M108 92h122v16H108Z"/>
            <path class="bdr-tool-art__flow" d="M247 83h24l12 12h18m-7-5 7 5-7 5"/>
            <rect class="bdr-tool-art__comment" x="272" y="111" width="145" height="77" rx="8"/>
            <path class="bdr-tool-art__comment-line" d="M290 132h94m-94 14h68"/>
            <circle class="bdr-tool-art__approval" cx="397" cy="181" r="20"/><path class="bdr-tool-art__check" d="m388 181 6 6 12-13"/>
          </svg>
          <div class="bdr-tool-art__caption"><span>Код</span><span aria-hidden="true">→</span><span>Ревью с ИИ</span><span aria-hidden="true">→</span><strong>Ваше решение</strong></div>
        </div>
        <div class="bdr-tool-card__body">
          <div class="bdr-tool-card__title"><h3><a href="https://bedrock-python.github.io/mr-review/">mr-review</a></h3><span class="bdr-tool-card__type">НА ВАШЕМ СЕРВЕРЕ</span></div>
          <h4>Ревью кода под вашим контролем.</h4>
          <p>Ревью с помощью ИИ для GitLab, GitHub, Gitea, Forgejo и Bitbucket. Четыре этапа проверки и веб-интерфейс: каждый комментарий публикуется только после вашего одобрения.</p>
          <div class="bdr-tool-tags"><span>Claude &amp; OpenAI</span><span>Совместимые модели</span><span>Одобрение человеком</span></div>
          <div class="bdr-tool-card__links"><a class="bdr-tool-primary" href="https://bedrock-python.github.io/mr-review/">Открыть mr-review <span aria-hidden="true">↗</span></a><a class="bdr-tool-source" href="https://github.com/bedrock-python/mr-review">GitHub <span aria-hidden="true">↗</span></a></div>
        </div>
        <div class="bdr-tool-card__meta"><span>Бэкенд на Python 3.12</span><span>Docker · образы на GHCR</span></div>
      </article>

      <article class="bdr-tool-card bdr-tool-card--mattermind" id="mattermind">
        <div class="bdr-tool-art bdr-tool-art--mattermind" aria-hidden="true">
          <div class="bdr-tool-art__label"><span>КОНТЕКСТ И ИСТОЧНИКИ</span><span>02</span></div>
          <svg class="bdr-tool-mattermind-drawing" viewBox="0 0 480 220" fill="none">
            <path class="bdr-tool-art__guide" d="M40 175h400M105 25v165M375 25v165"/>
            <rect class="bdr-tool-art__paper" x="80" y="38" width="243" height="54" rx="9"/>
            <path class="bdr-tool-art__code" d="M127 59h151m-151 14h101"/>
            <circle class="bdr-tool-art__question" cx="105" cy="64" r="10"/>
            <path class="bdr-tool-art__flow" d="M291 92v20m-5-6 5 6 5-6"/>
            <rect class="bdr-tool-art__comment" x="149" y="118" width="257" height="75" rx="9"/>
            <path class="bdr-tool-art__comment-line" d="M169 139h195m-195 14h136"/>
            <rect class="bdr-tool-art__citation" x="169" y="168" width="44" height="11" rx="3"/><rect class="bdr-tool-art__citation" x="220" y="168" width="44" height="11" rx="3"/><rect class="bdr-tool-art__citation" x="271" y="168" width="44" height="11" rx="3"/>
            <path class="bdr-tool-art__accent-line" d="m78 135-12 12 12 12m19-24 12 12-12 12"/>
          </svg>
          <div class="bdr-tool-art__caption"><span>Вопрос</span><span aria-hidden="true">→</span><span>Поиск в переписке</span><span aria-hidden="true">→</span><strong>Ответ и источники</strong></div>
        </div>
        <div class="bdr-tool-card__body">
          <div class="bdr-tool-card__title"><h3><a href="https://bedrock-python.github.io/mattermind/">mattermind</a></h3><a class="bdr-tool-version" data-pypi="mattermind" href="https://pypi.org/project/mattermind/" title="mattermind на PyPI">v0.1.1</a></div>
          <h4>Ответ уже есть в вашей переписке.</h4>
          <p>Задавайте вопросы о своём рабочем пространстве Mattermost обычным языком. ИИ-агент ищет по обсуждениям и подкрепляет каждый вывод прямой ссылкой на источник.</p>
          <div class="bdr-tool-tags"><span>Полнотекстовый поиск</span><span>Чат в терминале</span><span>Вывод JSON</span></div>
          <div class="bdr-tool-card__links"><a class="bdr-tool-primary" href="https://bedrock-python.github.io/mattermind/">Открыть mattermind <span aria-hidden="true">↗</span></a><a class="bdr-tool-source" href="https://github.com/bedrock-python/mattermind">GitHub <span aria-hidden="true">↗</span></a></div>
        </div>
        <div class="bdr-tool-card__meta"><span>Python 3.12+</span><code>uv tool install mattermind</code></div>
      </article>
    </div>
  </section>

  <section class="bdr-tool-section" id="from-libraries" aria-labelledby="cli-title">
    <div class="bdr-tool-section__heading"><div><span>02 / ИЗ БИБЛИОТЕК</span><h2 id="cli-title">Библиотека и самостоятельный инструмент.</h2></div><p>Для скриптов, CronJob и командной строки.</p></div>
    <article class="bdr-tool-cli">
      <div class="bdr-tool-terminal" aria-label="Возможности CLI pg-partsmith">
        <div class="bdr-tool-terminal__bar"><span aria-hidden="true">● ● ●</span><span>pg-partsmith / CLI</span></div>
        <div class="bdr-tool-terminal__body"><span class="bdr-tool-terminal__label">ОПЕРАЦИИ С СЕКЦИЯМИ</span><div class="bdr-tool-terminal__commands"><span>plan</span><span>apply</span><span>validate</span><span>backfill</span></div><div class="bdr-tool-partitions" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div><p>Документ YAML.<br>План, который можно проверить заранее.</p></div>
      </div>
      <div class="bdr-tool-cli__body">
        <div class="bdr-tool-card__title"><h3><a href="https://bedrock-python.github.io/pg-partsmith/guide/cli/">pg-partsmith CLI</a></h3><a class="bdr-tool-version" data-pypi="pg-partsmith" href="https://pypi.org/project/pg-partsmith/" title="pg-partsmith на PyPI">v1.5.0</a></div>
        <p>Планируйте, создавайте, проверяйте и заполняйте секции PostgreSQL по документу YAML. Коды завершения для CronJob и контейнерный образ для стеков без Python.</p>
        <div class="bdr-tool-tags"><span>Python 3.11+</span><span>Библиотека + CLI + контейнер</span></div>
        <div class="bdr-tool-cli__install"><span>УСТАНОВКА</span><code>pip install "pg-partsmith[cli]"</code></div>
        <div class="bdr-tool-card__links"><a class="bdr-tool-primary" href="https://bedrock-python.github.io/pg-partsmith/guide/cli/">Руководство по CLI <span aria-hidden="true">↗</span></a><a class="bdr-tool-source" href="https://github.com/bedrock-python/pg-partsmith">GitHub <span aria-hidden="true">↗</span></a></div>
        <div class="bdr-tool-cli__image">Контейнер: <code>ghcr.io/bedrock-python/pg-partsmith</code></div>
      </div>
    </article>
  </section>
  <a class="bdr-tool-more" href="../libraries/"><span><strong>Нужна интеграция в приложение?</strong><span>Посмотрите библиотеки Python, на которых работают инструменты.</span></span><span aria-hidden="true">Открыть библиотеки ↗</span></a>
</div>
