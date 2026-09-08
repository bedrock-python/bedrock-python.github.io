---
title: Bedrock Python
description: Production-grade Python libraries and developer tools for the infrastructure layer of modern backend services.
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
    <div class="bdr-home-hero__eyebrow"><span></span> The Bedrock Python ecosystem</div>
    <h1 id="home-title">Foundations for<br>serious <em>Python</em><br>services.</h1>
    <p class="bdr-home-hero__lede">Open-source libraries for the infrastructure behind your service. Runtime, clients, data and reliability — built for the same production stack.</p>
    <div class="bdr-home-hero__actions">
      <a class="bdr-btn bdr-btn--primary" href="libraries/">Explore the libraries <span aria-hidden="true">↗</span></a>
      <a class="bdr-home-hero__blog" href="blog/">Read the engineering blog <span aria-hidden="true">→</span></a>
    </div>
    <div class="bdr-home-hero__proof">
      <a href="libraries/"><strong>12</strong> libraries</a><span aria-hidden="true">/</span>
      <a href="tools/"><strong>2</strong> developer tools</a><span aria-hidden="true">/</span>
      <span>Open source</span>
    </div>
  </div>
  <figure class="bdr-stack" aria-labelledby="stack-caption">
    <div class="bdr-stack__heading"><span class="bdr-stack__index">01 — 04</span><span>Independent pieces. Shared foundations.</span></div>
    <!-- SVG links use xlink so instant navigation leaves their read-only href properties intact. -->
    <svg class="bdr-stack__diagram" viewBox="0 0 600 470" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-label="Explore four groups of Bedrock Python libraries">
      <defs>
        <pattern id="bdr-stack-dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="currentColor"/></pattern>
        <radialGradient id="bdr-stack-fade"><stop offset="0" stop-color="white"/><stop offset="1" stop-color="black"/></radialGradient>
        <mask id="bdr-stack-mask"><rect width="600" height="470" fill="url(#bdr-stack-fade)"/></mask>
      </defs>
      <g aria-hidden="true">
        <rect class="bdr-stack__dots" width="600" height="470" fill="url(#bdr-stack-dots)" mask="url(#bdr-stack-mask)"/>
        <path class="bdr-stack__floor" d="m46 354 170-85 170 85-170 85-170-85Zm34 17 170-85m-136 102 170-85m-136 102 170-85m-136 102 170-85M80 337l170 85M114 320l170 85M148 303l170 85M182 286l170 85"/>
        <path class="bdr-stack__axis" d="M216 42v383M76 137v217M356 137v217"/>
        <text class="bdr-stack__service-label" x="216" y="30" text-anchor="middle">YOUR PYTHON SERVICE</text>
        <path class="bdr-stack__service-line" d="M216 40v23"/>
      </g>
      <a class="bdr-stack__layer bdr-stack__layer--database" xlink:href="libraries/#database" aria-label="Database operations: partitions and migration tests">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 318 140 70v19L76 337Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 388 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 248 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 264 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__surface-detail" d="m132 306 84 42 84-42m-168 12 84 42 84-42"/>
        </g>
        <path class="bdr-stack__connector" d="M356 325h30l12 12h16"/>
        <circle class="bdr-stack__port" cx="356" cy="325" r="3"/>
        <text class="bdr-stack__number" x="420" y="319">04 / OPERATE</text>
        <text class="bdr-stack__label" x="420" y="342">Database operations</text>
        <text class="bdr-stack__description" x="420" y="362">Partitions · migrations</text>
        <path class="bdr-stack__link-arrow" d="M565 319h8v8m-8 0 8-8"/>
      </a>
      <a class="bdr-stack__layer bdr-stack__layer--reliability" xlink:href="libraries/#reliability" aria-label="Reliability patterns: outbox, idempotency and deadlines">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 257 140 70v19L76 276Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 327 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 187 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 203 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__surface-detail" d="m167 266 22 11 20-25 22 11 34-10"/>
        </g>
        <path class="bdr-stack__connector" d="M356 264h58"/>
        <circle class="bdr-stack__port" cx="356" cy="264" r="3"/>
        <text class="bdr-stack__number" x="420" y="246">03 / PROTECT</text>
        <text class="bdr-stack__label" x="420" y="269">Reliability patterns</text>
        <text class="bdr-stack__description" x="420" y="289">Outbox · keys · deadlines</text>
        <path class="bdr-stack__link-arrow" d="M565 246h8v8m-8 0 8-8"/>
      </a>
      <a class="bdr-stack__layer bdr-stack__layer--data" xlink:href="libraries/#data" aria-label="Data and messaging: PostgreSQL, Redis and Kafka">
        <g class="bdr-stack__block">
          <path class="bdr-stack__face bdr-stack__face--left" d="m76 196 140 70v19L76 215Z"/>
          <path class="bdr-stack__face bdr-stack__face--right" d="m216 266 140-70v19l-140 70Z"/>
          <path class="bdr-stack__top" d="m216 126 140 70-140 70-140-70Z"/>
          <path class="bdr-stack__inset" d="m216 142 108 54-108 54-108-54Z"/>
          <path class="bdr-stack__surface-detail" d="m158 202 20-10 20 10-20 10-20-10Zm39 20 20-10 20 10-20 10-20-10Zm40-20 20-10 20 10-20 10-20-10Z"/>
        </g>
        <path class="bdr-stack__connector" d="M356 203h30l12-12h16"/>
        <circle class="bdr-stack__port" cx="356" cy="203" r="3"/>
        <text class="bdr-stack__number" x="420" y="173">02 / CONNECT</text>
        <text class="bdr-stack__label" x="420" y="196">Data &amp; messaging</text>
        <text class="bdr-stack__description" x="420" y="216">Postgres · Redis · Kafka</text>
        <path class="bdr-stack__link-arrow" d="M565 173h8v8m-8 0 8-8"/>
      </a>
      <a class="bdr-stack__layer bdr-stack__layer--runtime" xlink:href="libraries/#runtime" aria-label="Runtime and transports: services, HTTP and gRPC">
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
        <text class="bdr-stack__number" x="420" y="100">01 / BUILD</text>
        <text class="bdr-stack__label" x="420" y="123">Runtime &amp; transports</text>
        <text class="bdr-stack__description" x="420" y="143">Services · HTTP · gRPC</text>
        <path class="bdr-stack__link-arrow" d="M565 100h8v8m-8 0 8-8"/>
      </a>
      <g class="bdr-stack__base-note" aria-hidden="true"><path d="M192 434h48"/><text x="216" y="455" text-anchor="middle">BUILT ON BEDROCK</text></g>
    </svg>
    <nav class="bdr-stack__mobile" aria-label="Explore the service foundations">
      <a href="libraries/#runtime"><span class="bdr-stack__mobile-number" data-layer="runtime">01</span><span><strong>Runtime &amp; transports</strong><small>Services · HTTP · gRPC</small></span><span aria-hidden="true">↗</span></a>
      <a href="libraries/#data"><span class="bdr-stack__mobile-number" data-layer="data">02</span><span><strong>Data &amp; messaging</strong><small>Postgres · Redis · Kafka</small></span><span aria-hidden="true">↗</span></a>
      <a href="libraries/#reliability"><span class="bdr-stack__mobile-number" data-layer="reliability">03</span><span><strong>Reliability patterns</strong><small>Outbox · keys · deadlines</small></span><span aria-hidden="true">↗</span></a>
      <a href="libraries/#database"><span class="bdr-stack__mobile-number" data-layer="database">04</span><span><strong>Database operations</strong><small>Partitions · migrations</small></span><span aria-hidden="true">↗</span></a>
    </nav>
    <figcaption id="stack-caption"><span class="bdr-stack__caption-dot" aria-hidden="true"></span>Choose a layer to explore<span class="bdr-stack__caption-end" aria-hidden="true">↗</span></figcaption>
  </figure>
</section>

<section class="bdr-featured" markdown="0">
  <a class="bdr-featured__visual bdr-home-featured-art" href="blog/posts/2026-09-06-pg-partsmith/" aria-label="Read Managing PostgreSQL partitions, one failure at a time"></a>
  <div>
    <div class="bdr-featured__eyebrow">Featured · Libraries</div>
    <h2 class="bdr-featured__title">
      <a href="blog/posts/2026-09-06-pg-partsmith/">Managing PostgreSQL partitions, one failure at a time</a>
    </h2>
    <p class="bdr-featured__lede">
      Two ways a partitioned table gets you out of bed, and the library that grew out of
      them: a plan you can read before it runs, ownership that never drops a table it did
      not make, the same API async and sync, a command line and a container image for
      teams with no Python, hooks from a YAML document, and one page for the AI assistant
      doing the wiring.
    </p>
    <div class="bdr-featured__meta">
      <span>September 6, 2026</span>
      <span>·</span>
      <span>Libraries · Tools</span>
    </div>
  </div>
</section>

<section markdown="0">
  <div class="bdr-section-head">
    <h2 class="bdr-section-head__title">Latest from the blog</h2>
    <a class="bdr-section-head__link" href="blog/">See all posts →</a>
  </div>

  <div class="bdr-grid">
    <a class="bdr-card" href="blog/posts/2026-09-07-zero-dependency-cores/">
      <div class="bdr-card__visual bdr-card__visual--design"></div>
      <div class="bdr-card__eyebrow">Design</div>
      <h3 class="bdr-card__title">Zero-dependency cores</h3>
      <p class="bdr-card__lede">
        An infrastructure library ends up in every service, and so does every dependency
        it declares. Measured: three of eight install exactly one distribution, and the FastAPI
        extra adds twenty-two.
      </p>
      <div class="bdr-card__meta">September 7, 2026</div>
    </a>

    <a class="bdr-card" href="blog/posts/2026-09-07-how-i-start-a-production-grade-python-library/">
      <div class="bdr-card__visual bdr-card__visual--meta"></div>
      <div class="bdr-card__eyebrow">Meta</div>
      <h3 class="bdr-card__title">How I start a production-grade Python library in 2026</h3>
      <p class="bdr-card__lede">
        One command, forty-one files, a green gate in three seconds. What each group of
        files decides, and the line of configuration that selected a rule family and then
        ignored it.
      </p>
      <div class="bdr-card__meta">September 7, 2026</div>
    </a>

    <a class="bdr-card" href="blog/posts/2026-09-07-migrating-from-pg-partman/">
      <div class="bdr-card__visual bdr-card__visual--tutorials"></div>
      <div class="bdr-card__eyebrow">Tutorials</div>
      <h3 class="bdr-card__title">Migrating from pg_partman to application-managed partitions</h3>
      <p class="bdr-card__lede">
        What happens to the partitions that already exist? Measured against pg_partman
        5.5: nothing. Both maintainers run side by side, and ownership is decided by bounds
        rather than names.
      </p>
      <div class="bdr-card__meta">September 7, 2026</div>
    </a>
























  </div>
</section>

<section class="bdr-home-pathways" aria-labelledby="home-pathways-title" markdown="0">
  <div class="bdr-home-pathways__heading">
    <div>
      <div class="bdr-home-pathways__eyebrow">FROM READING TO BUILDING</div>
      <h2 id="home-pathways-title">Put the ideas to work.</h2>
    </div>
    <p>Pick a task. Find the right starting point.</p>
  </div>
  <div class="bdr-home-pathways__grid">
    <article class="bdr-home-path bdr-home-path--libraries" aria-labelledby="home-libraries-title">
      <div class="bdr-home-path__intro">
        <div class="bdr-home-path__heading">
          <div>
            <span class="bdr-home-path__label">01 / LIBRARIES</span>
            <h3 id="home-libraries-title">Build your service.</h3>
          </div>
          <span class="bdr-home-path__icon" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><path d="m16 4 11 6-11 6-11-6 11-6Zm-11 6v12l11 6 11-6V10M16 16v12M5 16l11 6 11-6"/></svg></span>
        </div>
        <p>Composable Python foundations for your runtime, data and reliability.</p>
      </div>
      <nav class="bdr-home-path__routes" aria-label="Find a library by task">
        <a href="libraries/#runtime"><span>Run a Python service</span><small>Runtime · HTTP · gRPC</small><span aria-hidden="true">↗</span></a>
        <a href="libraries/#data"><span>Connect your data</span><small>Postgres · Redis · Kafka</small><span aria-hidden="true">↗</span></a>
        <a href="libraries/#reliability"><span>Make work reliable</span><small>Outbox · keys · deadlines</small><span aria-hidden="true">↗</span></a>
      </nav>
      <a class="bdr-home-path__all" href="libraries/">Explore all libraries <span aria-hidden="true">→</span></a>
    </article>
    <article class="bdr-home-path bdr-home-path--tools" aria-labelledby="home-tools-title">
      <div class="bdr-home-path__intro">
        <div class="bdr-home-path__heading">
          <div>
            <span class="bdr-home-path__label">02 / TOOLS</span>
            <h3 id="home-tools-title">Clear the busywork.</h3>
          </div>
          <span class="bdr-home-path__icon" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><rect x="4" y="6" width="24" height="20" rx="3"/><path d="M4 12h24m-17 5 3 3-3 3m7 0h5"/><path d="M8 9h.01M11 9h.01"/></svg></span>
        </div>
        <p>Focused tools to review code, find answers and plan database changes.</p>
      </div>
      <nav class="bdr-home-path__routes" aria-label="Find a developer tool by task">
        <a href="tools/#mr-review"><span>Review code</span><small>mr-review</small><span aria-hidden="true">↗</span></a>
        <a href="tools/#mattermind"><span>Search your workspace</span><small>mattermind</small><span aria-hidden="true">↗</span></a>
        <a href="tools/#from-libraries"><span>Plan a database change</span><small>pg-partsmith CLI</small><span aria-hidden="true">↗</span></a>
      </nav>
      <a class="bdr-home-path__all" href="tools/">Explore all tools <span aria-hidden="true">→</span></a>
    </article>
  </div>
</section>
