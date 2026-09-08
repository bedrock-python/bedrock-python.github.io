---
title: Tools
description: Developer tools for thoughtful code reviews, answers from your workspace, and PostgreSQL operations. Built with Python, ready for your workflow.
hide:
  - navigation
  - toc
---

<div class="bdr-tools-page" markdown="0">
  <header class="bdr-tool-hero">
    <div class="bdr-tool-hero__copy">
      <div class="bdr-tool-eyebrow"><span></span> THE WORKBENCH / DEVELOPER TOOLS</div>
      <h1>Less busywork.<br><em>More building.</em></h1>
      <p>Review the change. Find the context. Plan the next operation. Focused tools for the work around your code, with Python underneath.</p>
      <div class="bdr-tool-hero__principles"><span>Self-hosted</span><span>Open source</span><span>Built for real workflows</span></div>
    </div>
    <nav class="bdr-tool-jumps" aria-label="Find a tool for your task">
      <div class="bdr-tool-jumps__label">WHAT ARE YOU WORKING ON?</div>
      <a href="#mr-review"><span class="bdr-tool-jumps__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M6 6v12m12-12v5a5 5 0 0 1-5 5H6"/><circle cx="6" cy="4" r="2"/><circle cx="6" cy="20" r="2"/><circle cx="18" cy="4" r="2"/></svg></span><span><strong>Review a change</strong><small>mr-review</small></span><span aria-hidden="true">↗</span></a>
      <a href="#mattermind"><span class="bdr-tool-jumps__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M20 14a3 3 0 0 1-3 3H9l-5 4V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v8Z"/><path d="M8 8h8m-8 4h5"/></svg></span><span><strong>Find the answer</strong><small>mattermind</small></span><span aria-hidden="true">↗</span></a>
      <a href="#from-libraries"><span class="bdr-tool-jumps__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3m6 0h4"/></svg></span><span><strong>Plan a database change</strong><small>pg-partsmith CLI</small></span><span aria-hidden="true">↗</span></a>
    </nav>
  </header>

  <section class="bdr-tool-section" id="standalone" aria-labelledby="standalone-title">
    <div class="bdr-tool-section__heading"><div><span>01 / STANDALONE</span><h2 id="standalone-title">Ready for your workflow.</h2></div><p>Install, connect, get to work.</p></div>
    <div class="bdr-tool-grid">
      <article class="bdr-tool-card bdr-tool-card--review" id="mr-review">
        <div class="bdr-tool-art bdr-tool-art--review" aria-hidden="true">
          <div class="bdr-tool-art__label"><span>THOUGHTFUL CODE REVIEW</span><span>01</span></div>
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
          <div class="bdr-tool-art__caption"><span>Code</span><span aria-hidden="true">→</span><span>AI review</span><span aria-hidden="true">→</span><strong>Your approval</strong></div>
        </div>
        <div class="bdr-tool-card__body">
          <div class="bdr-tool-card__title"><h3><a href="https://bedrock-python.github.io/mr-review/">mr-review</a></h3><span class="bdr-tool-card__type">SELF-HOSTED APP</span></div>
          <h4>Code review, with you in control.</h4>
          <p>AI-assisted reviews for GitLab, GitHub, Gitea, Forgejo and Bitbucket. A four-stage review and a web UI, with every comment approved by you before it is posted.</p>
          <div class="bdr-tool-tags"><span>Claude &amp; OpenAI</span><span>Compatible models</span><span>Human approval</span></div>
          <div class="bdr-tool-card__links"><a class="bdr-tool-primary" href="https://bedrock-python.github.io/mr-review/">Explore mr-review <span aria-hidden="true">↗</span></a><a class="bdr-tool-source" href="https://github.com/bedrock-python/mr-review">GitHub <span aria-hidden="true">↗</span></a></div>
        </div>
        <div class="bdr-tool-card__meta"><span>Python 3.12 backend</span><span>Docker · images on GHCR</span></div>
      </article>

      <article class="bdr-tool-card bdr-tool-card--mattermind" id="mattermind">
        <div class="bdr-tool-art bdr-tool-art--mattermind" aria-hidden="true">
          <div class="bdr-tool-art__label"><span>CONTEXT, WITH SOURCES</span><span>02</span></div>
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
          <div class="bdr-tool-art__caption"><span>Ask</span><span aria-hidden="true">→</span><span>Search the workspace</span><span aria-hidden="true">→</span><strong>Answer + sources</strong></div>
        </div>
        <div class="bdr-tool-card__body">
          <div class="bdr-tool-card__title"><h3><a href="https://bedrock-python.github.io/mattermind/">mattermind</a></h3><a class="bdr-tool-version" data-pypi="mattermind" href="https://pypi.org/project/mattermind/" title="mattermind on PyPI">v0.1.1</a></div>
          <h4>Your workspace has the answer.</h4>
          <p>Ask your Mattermost workspace questions in plain language. An agentic loop searches conversations and cites every claim with a permalink, so you can follow the answer back to its source.</p>
          <div class="bdr-tool-tags"><span>Full-text search</span><span>Chat TUI</span><span>JSON output</span></div>
          <div class="bdr-tool-card__links"><a class="bdr-tool-primary" href="https://bedrock-python.github.io/mattermind/">Explore mattermind <span aria-hidden="true">↗</span></a><a class="bdr-tool-source" href="https://github.com/bedrock-python/mattermind">GitHub <span aria-hidden="true">↗</span></a></div>
        </div>
        <div class="bdr-tool-card__meta"><span>Python 3.12+</span><code>uv tool install mattermind</code></div>
      </article>
    </div>
  </section>

  <section class="bdr-tool-section" id="from-libraries" aria-labelledby="cli-title">
    <div class="bdr-tool-section__heading"><div><span>02 / FROM THE LIBRARIES</span><h2 id="cli-title">A library. And a tool in its own right.</h2></div><p>For scripts, CronJobs, and the command line.</p></div>
    <article class="bdr-tool-cli">
      <div class="bdr-tool-terminal" aria-label="pg-partsmith CLI capabilities">
        <div class="bdr-tool-terminal__bar"><span aria-hidden="true">● ● ●</span><span>pg-partsmith / CLI</span></div>
        <div class="bdr-tool-terminal__body"><span class="bdr-tool-terminal__label">PARTITION OPERATIONS</span><div class="bdr-tool-terminal__commands"><span>plan</span><span>apply</span><span>validate</span><span>backfill</span></div><div class="bdr-tool-partitions" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div><p>A YAML document.<br>A plan you can read before it runs.</p></div>
      </div>
      <div class="bdr-tool-cli__body">
        <div class="bdr-tool-card__title"><h3><a href="https://bedrock-python.github.io/pg-partsmith/guide/cli/">pg-partsmith CLI</a></h3><a class="bdr-tool-version" data-pypi="pg-partsmith" href="https://pypi.org/project/pg-partsmith/" title="pg-partsmith on PyPI">v1.5.0</a></div>
        <p>Plan, apply, validate and backfill PostgreSQL partitions from a YAML document. Exit codes a CronJob can read, plus a container image for stacks with no Python in them.</p>
        <div class="bdr-tool-tags"><span>Python 3.11+</span><span>Library + CLI + container</span></div>
        <div class="bdr-tool-cli__install"><span>INSTALL</span><code>pip install "pg-partsmith[cli]"</code></div>
        <div class="bdr-tool-card__links"><a class="bdr-tool-primary" href="https://bedrock-python.github.io/pg-partsmith/guide/cli/">Read the CLI guide <span aria-hidden="true">↗</span></a><a class="bdr-tool-source" href="https://github.com/bedrock-python/pg-partsmith">GitHub <span aria-hidden="true">↗</span></a></div>
        <div class="bdr-tool-cli__image">Container: <code>ghcr.io/bedrock-python/pg-partsmith</code></div>
      </div>
    </article>
  </section>
  <a class="bdr-tool-more" href="../libraries/"><span><strong>Building inside your application?</strong><span>Explore the Python libraries behind the tools.</span></span><span aria-hidden="true">Explore libraries ↗</span></a>
</div>
