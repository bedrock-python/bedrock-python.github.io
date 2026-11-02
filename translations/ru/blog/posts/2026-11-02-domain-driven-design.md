---
date: 2026-11-02
authors:
  - stas
  - alex
author: Станислав Шимоволос, Алексей Шалаев
categories:
  - Design
tags:
  - ddd
  - domain-driven-design
  - architecture
  - testing
  - sqlalchemy-foundation-kit
  - omni-box
---

# Domain-Driven Design: сначала модель, потом паттерны {#domain-driven-design}

<p class="bdr-post__byline"><a href="https://github.com/stanislaushimovolos">Станислав Шимоволос</a> и <a href="https://github.com/AlexeyShalaev">Алексей Шалаев</a></p>

<div class="bdr-post__hero" data-bdr-post="2026-11-02-domain-driven-design" role="img" aria-label="Отдельные контексты хранят свои модели, и всё сходится к одной модели core в центре" markdown="0"></div>

В каждом серьёзном сервисе есть правила, которые придумали не разработчики: когда клиенту положена скидка, кто считается сотрудником, сколько груза можно взять сверх нормы.

Пока таких правил десяток, их держат в голове и в паре `if`. Когда их сотни и бизнес меняет их каждый квартал, код без общей картины начинает сопротивляться: правка в одном месте ломает три других, а на встречах разработчики и эксперты не понимают друг друга. Domain-Driven Design, или DDD, это набор принципов как раз для таких сервисов. Сложность в них не в нагрузке, а в самой предметной области, и код строится вокруг её модели, а не вокруг таблиц и эндпоинтов.

Статья выросла из доклада, который один из нас читал для команды, где вместе работают бэкендеры, ML-инженеры и аналитики. Вопросы из зала оказались не хуже слайдов, многие из них вошли в текст.

Идеи DDD принято делить на два уровня. Стратегические отвечают на вопрос, что и где моделировать: какая у системы модель и язык, где проходят границы контекстов, какие части важны для бизнеса и куда вкладывать силы. Тактические отвечают на вопрос, как выразить модель в коде внутри одного контекста: value objects, сущности, агрегаты, репозитории, доменные события. У Эванса тактика идёт во второй части книги, а стратегия только в последней, четвёртой, и спорят обычно именно о тактике. Мы идём в обратном порядке: сначала стратегия (модель, язык, границы, субдомены), потом принципы, которые связывают её с кодом (инварианты и трилемма), и в конце тактика.

Сразу пара оговорок. Мы не эксперты по DDD и не пересказываем синюю книгу, это обзор ключевых идей с нашими оценками. DDD к тому же одна из самых холиварных тем в разработке: почти у каждого тезиса здесь есть уважаемые противники, и где они есть, мы их называем. Примеры рассчитаны на Python 3.12 и новее. Код из статьи проверен [практикумом](../lab/2026-11-02-domain-driven-design/README.md) на Python 3.13, SQLAlchemy 2.1.6, sqlalchemy-foundation-kit 0.5.1, omni-box 0.3.1 и PostgreSQL 17.11.

<!-- more -->

## Модель важнее кода {#model}

Если оставить от DDD одну идею, то вот она: прежде чем писать фичу, её нужно уложить в модель.

Обычно задачу решают напрямую: пришло требование, нашли место в коде, дописали. В DDD между требованием и кодом есть ещё один шаг. Сначала садимся и разбираемся, какие в процессе есть сущности, что с ними происходит и как они взаимодействуют. На бумажке, на доске, в голове, неважно где. Получившаяся картина и есть модель предметной области (domain model): наше представление о том, как устроен этот кусок мира.

Хорошая аналогия есть в физике. Атом устроен сложно, и физики описывают его моделями: у Резерфорда электроны летают вокруг ядра, как планеты, потом пришла квантовая механика. Ни одна модель не «правда», но каждая полезна и каждая следующая точнее. В разработке так же: модель не обязана совпадать с реальностью, она обязана быть полезным упрощением.

Когда модель есть, фичи реализуются внутри неё. Нельзя просто дописать `if` или подпереть что-то костылём, если это не ложится на наши сущности. Сначала адаптируем модель под новое требование, потом пишем код. Код иногда расходится с реальностью, и тогда мы снова уточняем модель. Эванс называет это углубляющим рефакторингом (refactoring toward deeper insight).

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Цикл разработки по модели</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="0" data-search-exclude>
<svg class="bdr-svg" viewBox="0 0 440 424" role="img" aria-labelledby="ddd-cycle-title ddd-cycle-desc" xmlns="http://www.w3.org/2000/svg">
<title id="ddd-cycle-title">Цикл разработки по модели</title>
<desc id="ddd-cycle-desc">Знания экспертов перерабатываются в модель, модель прямо выражается в коде, а нестыковка кода с реальностью возвращает команду к экспертам и модели.</desc>
<defs>
<marker id="ddd-cycle-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head" d="M0,0 L10,5 L0,10 z"/></marker>
<marker id="ddd-cycle-head-accent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head bdr-svg__head--accent" d="M0,0 L10,5 L0,10 z"/></marker>
</defs>
<g class="bdr-svg__box"><rect x="170" y="20" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="45" text-anchor="middle">Предметная область</text><text class="bdr-svg__sub" x="295" y="64" text-anchor="middle">эксперты и реальный мир</text></g>
<g class="bdr-svg__box"><rect x="170" y="130" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="155" text-anchor="middle">Переработка знаний</text><text class="bdr-svg__sub" x="295" y="174" text-anchor="middle">knowledge crunching</text></g>
<g class="bdr-svg__box bdr-svg__box--strong"><rect x="170" y="240" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="265" text-anchor="middle">Модель</text><text class="bdr-svg__sub" x="295" y="284" text-anchor="middle">полезное упрощение</text></g>
<g class="bdr-svg__box"><rect x="170" y="350" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="375" text-anchor="middle">Код</text><text class="bdr-svg__sub" x="295" y="394" text-anchor="middle">прямое выражение модели</text></g>
<path class="bdr-svg__edge" d="M295 78 V127" marker-end="url(#ddd-cycle-head)"/>
<text class="bdr-svg__note" x="306" y="108">диалог с экспертами</text>
<path class="bdr-svg__edge" d="M295 188 V237" marker-end="url(#ddd-cycle-head)"/>
<text class="bdr-svg__note" x="306" y="218">дистилляция</text>
<path class="bdr-svg__edge" d="M295 298 V347" marker-end="url(#ddd-cycle-head)"/>
<text class="bdr-svg__note" x="306" y="328">трансляция в код</text>
<path class="bdr-svg__edge bdr-svg__edge--accent bdr-svg__edge--dashed" d="M170 379 H44 V49 H167" marker-end="url(#ddd-cycle-head-accent)"/>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="190">нестыковка</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="207">с реальностью:</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="224">углубляющий</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="241">рефакторинг</text>
</svg>
</div>
<p class="bdr-diagram__caption">Знания экспертов перерабатываются в модель, модель прямо выражается в коде, а нестыковка кода с реальностью возвращает команду к экспертам и модели.</p>
</figure>
<!-- /diagram:concept -->

Самое плохое, что можно сделать в таком цикле, это сломать модель. И самое ценное в проекте не код, а модель: то, как команда понимает задачу. Код важен, но он лишь её запись. Звучит абстрактно, но на практике это различие между «гоняем JSON из одной ручки в другую» и «решаем вот такую проблему вот такими понятиями». В большинстве сервисов, которые мы видели, модели нет: где-то что-то клепается, и никто не может сказать, какие правила для системы святы.

## Единый язык {#ubiquitous-language}

Второе по важности после модели: единый язык (ubiquitous language).

Один из нас раньше делал сервис для врачей. Врачи говорили своими терминами, разработчики своими, и на каждой встрече обе стороны вежливо кивали, не понимая друг друга. Врачи просили одно, разработчики пилили другое, и через пару месяцев выяснялось, что под одним словом все имели в виду разное.

Типичная цепочка переводов выглядит так. Эксперт говорит «покупатель оформляет заказ», аналитик пишет в задаче «пользователь создаёт заявку», а в коде появляется `session.add(order_row)`. На каждом переводе теряется часть смысла, и через год «заявка» в голове аналитика обрастает свойствами, которых у «заказа» эксперта нет.

Лечится это одним языком, который задаёт модель. Если в модели есть «заказ», «отгрузка» и «оплата», эти слова звучат на встречах, стоят в задачах, в названиях классов, методов и тестов. Если договорились говорить `customer`, никто не пишет `user`: иначе два слова начнут жить своей жизнью. Язык живой: стоит заметить нестыковку, правим язык и модель вместе и доносим правку до всех.

У языка есть граница применимости, и она подводит нас к следующей идее.

## Bounded Context: где заканчивается модель {#bounded-context}

Большую предметную область трудно описать одной моделью. Возьмём интернет-магазин: в нём есть каталог, склад и биллинг. В каждой из этих частей есть «товар», но это три разных товара. Для каталога это описание, фото и характеристики, для склада остатки, ячейка и вес, для биллинга цена, налоги и скидки. Попытка свести их в один класс `Product` даёт монстра, которого боится трогать каждая из трёх команд.

DDD предлагает другое: части предметной области (субдомены) отражаются в ограниченные контексты (bounded contexts). Bounded context обозначает границу, внутри которой действует одна модель со своим языком. Внутри контекста склада «товар» значит ровно одно. Контексты изолированы друг от друга и общаются по явным правилам.

Это логическое разделение, а не решение про деплой. Монолит из трёх модулей или три микросервиса, с точки зрения DDD неважно: важно, что у каждого контекста своя модель. В идеале один субдомен отражается в один контекст, но в жизни это соответствие бывает и не один к одному.

Как контексты связаны друг с другом, описывает карта контекстов (context map). У Эванса для этого целый набор отношений:

| Отношение | Что происходит |
|---|---|
| Shared Kernel | две команды делят небольшой общий кусок модели и меняют его только вместе |
| Customer / Supplier | поставщик (upstream) учитывает потребности потребителя (downstream) в своих планах |
| Conformist | потребитель принимает модель поставщика как есть, без перевода |
| Anticorruption Layer | потребитель переводит чужую модель в свою через слой адаптеров и не зависит от неё |
| Open Host Service, Published Language | поставщик публикует протокол и формат для многих потребителей сразу |
| Separate Ways | контексты не интегрируются вовсе |

На практике чаще всего встречаются два противоположных подхода. Anticorruption Layer, когда мы защищаем свою модель от чужой, и Conformist, когда контекст признаёт, что он менее важен, и просто живёт в чужих понятиях.

У Мартина Фаулера есть известная [иллюстрация](https://martinfowler.com/bliki/BoundedContext.html): контексты продаж и поддержки, и в обоих есть клиент и продукт. На вид сущности одинаковые, но у каждого контекста свой взгляд и свои атрибуты. Фаулер не предлагает объединять их: в каждом контексте своя модель общего понятия, а для интеграции между ними нужен маппинг. Значит, дублирование и в коде, и в базе нормально. Важнее слабая связанность между контекстами и сильная связность внутри.

На докладе мы назвали bounded context «ещё половиной процента успеха» после модели и языка. Справедливости ради: Вернон и Хононов ставят его в центр стратегического DDD, и как только у одного слова появляются два смысла или над системой работают две команды, мы с ними согласны.

## Core, supporting, generic: куда тратить силы {#subdomains}

Контексты делят систему по смыслу. Есть и второе деление: по важности для бизнеса. Субдомены бывают трёх типов.

**Core subdomain** отличает компанию от конкурентов, ради него она и существует. Возьмём сервис доставки еды. Его core составляют диспетчеризация курьеров, прогноз времени доставки и динамические цены. Именно алгоритм диспетчеризации, а не то, как курьеру приходит пуш.

Core требует настоящего моделирования, и в долгосрочной перспективе его пишут сами. Если бы готовый продукт закрывал наш core целиком, сам наш продукт был бы не нужен. Если закрывает частично, начинаются костыли. Попробуйте построить доставку еды на таск-трекере вроде Notion: там тоже есть карточки и статусы, но заказ не тикет. Лишнего много (спринты, story points), а нужного нет: геопозиции курьера, окна доставки, маршрута из нескольких заказов. Всё это придётся достраивать кастомными полями и скриптами. Эванс советует ставить на core лучших людей команды. Хороший повод честно спросить себя, кто у вас сейчас пишет диспетчеризацию.

Это не значит, что core пишут без фреймворков. Веб-фреймворк и ORM вокруг core вполне уместны. Плохо, когда модель core подгоняют под чужой продукт или фреймворк.

**Supporting subdomain** нужен и специфичен для бизнеса, но не уникален. У доставки это каталог ресторанов, кабинет ресторана, отзывы. Без них плохо, но конкурентное преимущество не в них. Простой тест из обсуждения на докладе: если оставить только core, продукт по-прежнему имеет смысл. Если оставить только supporting, всё бесполезно.

**Generic subdomain** покрывает типовые задачи, которые давно решены и есть у всех: оплату, авторизацию, уведомления. Их не изобретают: берут готовое решение, сервис или библиотеку.

Граница зависит от бизнеса. Уведомления курьерам остаются generic, пока ваше преимущество не в том, чтобы доставлять их быстрее и умнее всех. Если же именно в этом, уведомления становятся core. Классификация работает и за пределами бэкенда: ML-инженеры в зале быстро разложили свои задачи. В core у них попал пайплайн модели, в generic сохранение весов в safetensors и фреймворк распределённого обучения, а в supporting подготовка данных из десятка форматов, которую всё равно пишешь сам под конкретный проект.

Из этой классификации следует главный практический вывод: сколько DDD тратить на каждую часть. Хононов в «Learning Domain-Driven Design» прямо связывает тип субдомена со способом писать логику. Богатая доменная модель и вся тактика DDD окупаются в core. Для supporting часто хватает простого CRUD или transaction script. Generic берут готовым и прячут за адаптером. Применять DDD везде и одинаково значит гарантированно его возненавидеть.

Ещё был вопрос из зала: как это деление соотносится со слоями domain, application и infrastructure? Субдомены режут систему по важности, слои режут каждую часть по ответственности. Это ортогональные оси: внутри каждого контекста могут быть свои слои, и никакого противоречия тут нет. Причём набор слоёв у каждого свой. В core в центре стоит богатая доменная модель. В supporting часто хватает API и transaction script поверх таблиц. А generic вообще чужой сервис, и от него у нас остаётся только адаптер.

<!-- diagram:layers -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Слои внутри субдоменов</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="0" data-search-exclude>
<svg class="bdr-svg" viewBox="0 0 440 636" role="img" aria-labelledby="ddd-layers-title ddd-layers-desc" xmlns="http://www.w3.org/2000/svg">
<title id="ddd-layers-title">Слои внутри субдоменов</title>
<desc id="ddd-layers-desc">В core прикладной слой и инфраструктура зависят от доменной модели в центре, в supporting два слоя без доменной модели, а generic остаётся готовым сервисом, к которому core обращается через адаптер.</desc>
<defs>
<marker id="ddd-layers-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head" d="M0,0 L10,5 L0,10 z"/></marker>
<marker id="ddd-layers-hollow" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9" markerHeight="9" orient="auto"><path class="bdr-svg__head bdr-svg__head--hollow" d="M1,1 L11,6 L1,11 z"/></marker>
</defs>
<g class="bdr-svg__panel"><rect x="16" y="16" width="408" height="252" rx="12"/></g>
<text class="bdr-svg__title" x="36" y="44">Core: диспетчеризация</text>
<text class="bdr-svg__sub" x="36" y="63">богатая модель, вся тактика DDD</text>
<g class="bdr-svg__box"><rect x="36" y="78" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="97">Application</text><text class="bdr-svg__sub" x="52" y="114">сценарий «назначить курьера»</text></g>
<path class="bdr-svg__edge" d="M220 124 V143" marker-end="url(#ddd-layers-head)"/>
<text class="bdr-svg__note" x="232" y="138">вызывает</text>
<g class="bdr-svg__box bdr-svg__box--accent"><rect x="36" y="146" width="368" height="46" rx="8"/><text class="bdr-svg__name bdr-svg__name--accent" x="52" y="165">Domain</text><text class="bdr-svg__sub" x="52" y="182"><tspan class="bdr-svg__code">Order</tspan>, <tspan class="bdr-svg__code">Courier</tspan>, политика назначения</text></g>
<path class="bdr-svg__edge bdr-svg__edge--dashed" d="M220 214 V195" marker-end="url(#ddd-layers-hollow)"/>
<text class="bdr-svg__note" x="232" y="208">реализует интерфейсы</text>
<g class="bdr-svg__box"><rect x="36" y="214" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="233">Infrastructure</text><text class="bdr-svg__sub" x="52" y="250">репозитории и адаптеры</text></g>
<g class="bdr-svg__panel"><rect x="16" y="292" width="408" height="184" rx="12"/></g>
<text class="bdr-svg__title" x="36" y="320">Supporting: каталог ресторанов</text>
<text class="bdr-svg__sub" x="36" y="339">CRUD без тактического DDD</text>
<g class="bdr-svg__box"><rect x="36" y="354" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="373">API</text><text class="bdr-svg__sub" x="52" y="390">ручки кабинета ресторана</text></g>
<path class="bdr-svg__edge" d="M220 400 V419" marker-end="url(#ddd-layers-head)"/>
<g class="bdr-svg__box"><rect x="36" y="422" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="441">Transaction script</text><text class="bdr-svg__sub" x="52" y="458">SQL поверх таблиц, без доменной модели</text></g>
<g class="bdr-svg__panel"><rect x="16" y="500" width="408" height="120" rx="12"/></g>
<text class="bdr-svg__title" x="36" y="528">Generic: платежи</text>
<text class="bdr-svg__sub" x="36" y="547">берём готовое</text>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="36" y="562" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="581">Готовый платёжный сервис</text><text class="bdr-svg__sub" x="52" y="598">у нас только адаптер в инфраструктуре core</text></g>
</svg>
</div>
<p class="bdr-diagram__caption">В core прикладной слой и инфраструктура зависят от доменной модели в центре, в supporting два слоя без доменной модели, а generic остаётся готовым сервисом, к которому core обращается через адаптер.</p>
</figure>
<!-- /diagram:layers -->

## Зависимости смотрят на core {#dependencies}

Как это выглядит в коде. Core не зависит ни от чего. Ему нужны платежи и SMS, поэтому он объявляет интерфейсы `PaymentGateway` и `Notifier` на своём языке, а адаптеры в инфраструктуре реализуют их поверх конкретного вендора. Сменился платёжный провайдер, переписываем только адаптер. Это и есть Anticorruption Layer из таблицы выше, собранный через инверсию зависимостей.

Supporting-контекст (каталог ресторанов) поставляет core данные и события. Чтобы core не зависел от модели каталога, контракт задаёт core, а каталог его выполняет. Получается Customer / Supplier, где core в роли потребителя определяет, что ему нужно.

<!-- diagram:dependencies -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">ИДЕЯ В СХЕМЕ</span><strong>Зависимости направлены к core</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="0" data-search-exclude>
<svg class="bdr-svg" viewBox="0 0 440 604" role="img" aria-labelledby="ddd-deps-title ddd-deps-desc" xmlns="http://www.w3.org/2000/svg">
<title id="ddd-deps-title">Зависимости направлены к core</title>
<desc id="ddd-deps-desc">Core объявляет интерфейсы PaymentGateway и Notifier, адаптеры реализуют их поверх платёжного сервиса и SMS-шлюза, а каталог ресторанов передаёт core данные по контракту, который задаёт core.</desc>
<defs>
<marker id="ddd-deps-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head" d="M0,0 L10,5 L0,10 z"/></marker>
<marker id="ddd-deps-hollow" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9" markerHeight="9" orient="auto"><path class="bdr-svg__head bdr-svg__head--hollow" d="M1,1 L11,6 L1,11 z"/></marker>
</defs>
<g class="bdr-svg__panel bdr-svg__panel--accent"><rect x="16" y="128" width="408" height="190" rx="12"/></g>
<g class="bdr-svg__panel"><rect x="16" y="362" width="408" height="96" rx="12"/></g>
<g class="bdr-svg__panel"><rect x="16" y="490" width="408" height="98" rx="12"/></g>
<path class="bdr-svg__edge" d="M220 74 V125" marker-end="url(#ddd-deps-head)"/>
<path class="bdr-svg__edge bdr-svg__edge--dashed" d="M124 396 V303" marker-end="url(#ddd-deps-hollow)"/>
<path class="bdr-svg__edge bdr-svg__edge--dashed" d="M316 396 V303" marker-end="url(#ddd-deps-hollow)"/>
<path class="bdr-svg__edge" d="M124 440 V521" marker-end="url(#ddd-deps-head)"/>
<path class="bdr-svg__edge" d="M316 440 V521" marker-end="url(#ddd-deps-head)"/>
<g class="bdr-svg__box"><rect x="70" y="16" width="300" height="58" rx="10"/><text class="bdr-svg__name" x="220" y="41" text-anchor="middle">Supporting: каталог ресторанов</text><text class="bdr-svg__sub" x="220" y="60" text-anchor="middle">CRUD без тактического DDD</text></g>
<text class="bdr-svg__note" x="232" y="96">данные и события</text>
<text class="bdr-svg__note" x="232" y="112">по контракту core</text>
<text class="bdr-svg__title bdr-svg__title--accent" x="36" y="156">Core: диспетчеризация</text>
<text class="bdr-svg__sub" x="36" y="175">богатая модель предметной области</text>
<g class="bdr-svg__box"><rect x="36" y="188" width="112" height="34" rx="17"/><text class="bdr-svg__code" x="92" y="210" text-anchor="middle">Order</text></g>
<g class="bdr-svg__box"><rect x="164" y="188" width="112" height="34" rx="17"/><text class="bdr-svg__code" x="220" y="210" text-anchor="middle">Courier</text></g>
<g class="bdr-svg__box"><rect x="292" y="188" width="112" height="34" rx="17"/><text class="bdr-svg__code" x="348" y="210" text-anchor="middle">Restaurant</text></g>
<text class="bdr-svg__note" x="36" y="246">интерфейсы, которые объявляет core</text>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="36" y="256" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="124" y="283" text-anchor="middle">PaymentGateway</text></g>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="228" y="256" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="316" y="283" text-anchor="middle">Notifier</text></g>
<text class="bdr-svg__note" x="220" y="342" text-anchor="middle">реализуют</text>
<text class="bdr-svg__sub bdr-svg__halo" x="36" y="384">Anticorruption Layer в инфраструктуре</text>
<g class="bdr-svg__box"><rect x="36" y="396" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="124" y="423" text-anchor="middle">PaymentAdapter</text></g>
<g class="bdr-svg__box"><rect x="228" y="396" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="316" y="423" text-anchor="middle">SmsAdapter</text></g>
<text class="bdr-svg__note" x="220" y="478" text-anchor="middle">вызывают</text>
<text class="bdr-svg__sub bdr-svg__halo" x="36" y="512">Generic: готовые сервисы</text>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="36" y="524" width="176" height="44" rx="8"/><text class="bdr-svg__name" x="124" y="551" text-anchor="middle">Платёжный сервис</text></g>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="228" y="524" width="176" height="44" rx="8"/><text class="bdr-svg__name" x="316" y="551" text-anchor="middle">SMS-шлюз</text></g>
</svg>
</div>
<p class="bdr-diagram__caption">Core объявляет интерфейсы PaymentGateway и Notifier, адаптеры реализуют их поверх платёжного сервиса и SMS-шлюза, а каталог ресторанов передаёт core данные по контракту, который задаёт core.</p>
</figure>
<!-- /diagram:dependencies -->

Здесь DDD встречается с чистой, луковой и гексагональной архитектурами. DDD говорит, *что* изолировать: доменную модель. Архитектуры говорят, *как*: зависимости направлены внутрь, к модели, а база данных и UI становятся деталями. Любопытно, что у самого Эванса в 2003 году была классическая слоистая архитектура, где домен лежит над инфраструктурой и зависит от неё. Развернули зависимости позже: гексагональная архитектура Алистера Кокберна (2005), луковая Джеффри Палермо (2008), чистая Роберта Мартина (2012). Требование Эванса изолировать домен осталось, способ стал лучше.

## Богатая модель и анемичная {#rich-model}

Дальше начинается код, и разговор становится душнее.

Что такое модель с точки зрения кода? Набор объектов, которые поддерживают инварианты, то есть правила, которые мы сами сформулировали и считаем всегда верными. Хорошая доменная модель поддерживает много инвариантов. Другими словами, она инкапсулирована: Хориков определяет инкапсуляцию именно как защиту инвариантов, а не как сокрытие полей.

Противоположность хорошей модели называют анемичной. Данные лежат в одних объектах, логика в других: по сервису летают DTO, функции меняют их поля, и никакой структуры, кроме сигнатур, нет. Мы сами скатились к такой модели в одном из сервисов, когда торопились. Выглядит это так:

```python
@dataclass
class Person:
    name: str
    email: str
    is_employee: bool


class PersonService:
    def set_email(self, person: Person, email: str) -> None:
        person.email = email
        # is_employee depends on the email domain, but nobody updated it
```

Видно сразу две проблемы. Email не любая строка, а здесь в него можно записать что угодно. И `is_employee` зависит от email: если адрес на корпоративном домене, человек сотрудник. Это решение должен принимать сам `Person`, а здесь оно размазано по сервисам. Где-нибудь появится ещё один `update_person`, который поменяет email и забудет про флаг.

Тут важно не путать анемичную модель с transaction script. Transaction script, по Фаулеру, честный паттерн: одна процедура на одну бизнес-операцию. Для простой логики, например в supporting-субдомене, это отличный выбор. Анемичная модель получается, когда логика сложная, классы называются как сущности предметной области, а поведения в них нет. Фаулер [называет это антипаттерном](https://martinfowler.com/bliki/AnemicDomainModel.html): расходы на доменную модель вы несёте, а выгоды не получаете.

### Первый шаг: типы вместо примитивов {#value-types}

Самый дешёвый рефакторинг: заменить «тупые» строки и числа на типы предметной области.

```python
# Before: every service checks the rules, if it remembers to
@dataclass
class Customer:
    name: str
    email: str
    status: str
    current_discount: Decimal


# After: each rule lives in one type
@dataclass
class Customer:
    name: str
    email: Email
    status: Status
    current_discount: Discount
```

`Email`, `Status` и `Discount` здесь value objects, к ним мы ещё вернёмся. Пока достаточно того, что `Email` нельзя создать из невалидной строки. Есть шуточное название для кода на одних строках: stringly typed, в противовес strongly typed. Если value object пока заводить лень, в Python есть `typing.NewType`: проверок он не добавит, но смысл в сигнатурах станет виден.

### Второй шаг: поведение внутрь сущности {#behaviour}

Типы не спасают от изменяемого состояния. Допустим, клиент, у которого больше десяти заказов, получает статус Advanced:

```python
class CustomerService:
    def add_order(self, customer: Customer, product: Product, qty: int) -> None:
        customer.orders.append(Order(product, qty))
        if len(customer.orders) > 10:
            customer.status = Status.ADVANCED
```

Правило живёт в сервисе, и его легко обойти: любой код может дописать заказ в список или выставить статус руками. Если правило понадобится в двух местах или поменяется, его придётся искать по всему проекту. Хороший признак: внешний код вызывает у объекта один метод, и объект сам делает всё нужное. Если вызывающему приходится лезть внутрь и что-то проверять, инкапсуляции нет.

Переносим правило в сущность:

```python
class Customer:
    def __init__(self, name: str, email: Email) -> None:
        self._name = name
        self._email = email
        self._status = Status.REGULAR
        self._orders: list[Order] = []

    @property
    def status(self) -> Status:
        return self._status

    @property
    def orders(self) -> tuple[Order, ...]:
        return tuple(self._orders)

    def add_order(self, product: Product, qty: int) -> None:
        self._orders.append(Order(product, qty))
        if len(self._orders) > 10:
            self._status = Status.ADVANCED
```

Состояние снаружи только читается: статус через свойство, заказы как неизменяемый кортеж. В Python приватность держится на соглашении, и подчёркивание не остановит того, кто очень хочет. Но оно ясно говорит, где граница, а линтер и ревью её охраняют.

В итоге получается пирамида. Внизу value objects: в них большая часть логики, они неизменяемы и потому безопасны. Посередине сущности: они координируют value objects и держат инварианты. Сверху сервисы, которые только оркестрируют. Рефакторить начинаем снизу. Чем меньше изменяемого состояния и чем ближе мы к «сервис вызывает один метод сущности», тем лучше.

## Неявное сделать явным {#implicit-concepts}

Посмотрите на код бронирования груза на рейс. Пример из первой главы Эванса:

```python
def book(cargo: Cargo, voyage: Voyage) -> None:
    if voyage.booked + cargo.size > voyage.capacity * 1.1:
        raise BookingError(cargo, voyage)
    voyage.add(cargo)
```

Что за `1.1`? Это правило придумали не разработчики: судоходные компании принимают на 10% больше груза, чем вмещает судно, потому что часть клиентов в последний момент отказывается. У правила наверняка есть название, его обсуждают люди, оно описано в каком-то регламенте. Значит, ему место в модели под тем же именем:

```python
class OverbookingPolicy:
    """A voyage may be booked up to 10% over its capacity."""

    ratio = 1.1

    def allows(self, cargo: Cargo, voyage: Voyage) -> bool:
        return voyage.booked + cargo.size <= voyage.capacity * self.ratio


def book(cargo: Cargo, voyage: Voyage, policy: OverbookingPolicy) -> None:
    if not policy.allows(cargo, voyage):
        raise BookingError(cargo, voyage)
    voyage.add(cargo)
```

Строк стало больше, но правило теперь можно найти, обсудить с экспертом, протестировать отдельно и заменить. Если у правила нет имени, его нет в модели. Работает и в обратную сторону: вводим новое правило, наводим порядок в модели.

Где искать такие понятия, Эванс перечисляет в девятой главе: в языке экспертов (слово, которое они повторяют, а в коде его нет), в неуклюжем коде, который трудно объяснить, в противоречиях между тем, что говорят разные эксперты, и в литературе по предметной области.

## Функциональное ядро, императивная оболочка {#functional-core}

Следующий принцип известен под именем, которое придумал Гэри Бернхардт: functional core, imperative shell. Пример с системой аудита взят у Хорикова. Есть менеджер, который записывает визиты в файлы и начинает новый файл, когда текущий заполнен:

```python
class AuditManager:
    def add_record(self, visitor: str, time: datetime) -> None:
        files = sorted(self._directory.glob("audit_*.txt"))
        record = f"{visitor};{time.isoformat()}"
        if files:
            last = files[-1]
            lines = last.read_text().splitlines()
            if len(lines) < self._max_entries:
                last.write_text("\n".join([*lines, record]))
                return
        new_file = self._directory / f"audit_{len(files) + 1:04d}.txt"
        new_file.write_text(record)
```

На докладе кто-то сразу предложил вынести работу с хранилищем в отдельный класс. Это верное решение, но сначала стоит назвать проблему: здесь смешаны две задачи. Первая задача: правило «если файл заполнен, начинаем новый». Вторая: чтение и запись файлов. Правило не проверить без файловой системы, а тесты с файловой системой медленные и хрупкие.

Алгоритмическое ядро не должно ничего знать о вводе и выводе: только перемалывать одни данные в другие. Пусть ядро принимает содержимое файлов и возвращает решение, а выполняет его оболочка:

```python
@dataclass(frozen=True)
class FileContent:
    name: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class FileUpdate:
    name: str
    content: str


class AuditManager:
    def __init__(self, max_entries: int) -> None:
        self._max_entries = max_entries

    def add_record(self, files: Sequence[FileContent], visitor: str, time: datetime) -> FileUpdate:
        record = f"{visitor};{time.isoformat()}"
        if files and len(files[-1].lines) < self._max_entries:
            last = files[-1]
            return FileUpdate(last.name, "\n".join([*last.lines, record]))
        return FileUpdate(f"audit_{len(files) + 1:04d}.txt", record)


class AuditService:
    def add_record(self, visitor: str, time: datetime) -> None:
        files = self._persister.read_directory(self._directory)
        update = self._manager.add_record(files, visitor, time)
        self._persister.apply_update(self._directory, update)
```

Теперь правило проверяется обычным тестом на входные и выходные данные, без моков и без диска:

```python
def test_new_file_is_created_when_the_last_one_is_full() -> None:
    manager = AuditManager(max_entries=2)
    files = [FileContent("audit_0001.txt", ("Peter;2026-04-06T16:30:00", "Jane;2026-04-06T16:40:00"))]

    update = manager.add_record(files, "Alice", datetime(2026, 4, 6, 18, 0))

    assert update == FileUpdate("audit_0002.txt", "Alice;2026-04-06T18:00:00")
```

Отсюда простое правило для всего доменного слоя: в нём нет ни одного `await`. Появился `await`, значит, в домен протекло I/O.

## Трилемма: где проверять, что email свободен {#trilemma}

Эта часть вызвала на докладе больше всего споров, и не зря. Задача простая: пользователь меняет email, но только если адрес не занят другим пользователем. `User` у нас главная сущность, и её email не должен оказаться неконсистентным. Вопрос: кто решает, что адрес занят?

### Вариант 1: проверка в контроллере {#check-in-controller}

```python
class UserController:
    async def change_email(self, user_id: UUID, email: Email) -> str:
        other = await self._users.get_by_email(email)
        if other is not None and other.id != user_id:
            return "Email is taken"
        user = await self._users.get(user_id)
        user.change_email(email)
        await self._users.save(user)
        return "OK"
```

`User.change_email` про уникальность ничего не знает. Решение, что адрес можно занять, принимает внешний код, а не сущность. Где-нибудь появится `update_user`, который меняет сразу десяток полей и забывает про эту проверку. А если смена email однажды станет платной или начнёт начислять баллы, эта логика окажется размазанной по контроллерам. Модель изолирована и быстра, но не инкапсулирована.

### Вариант 2: репозиторий в домене {#repository-in-domain}

```python
class User:
    async def change_email(self, email: Email, users: UserRepository) -> None:
        other = await users.get_by_email(email)
        if other is not None and other.id != self.id:
            raise EmailTaken(email)
        self._email = email
```

Теперь решение принимает сама сущность, инкапсуляция на месте. Но реакция зала была единодушной: неприятно, что передаём репозиторий. Кто-то заметил, что репозитории теперь живут в двух слоях сразу, и в application, и в домене. Кто-то предложил передавать не репозиторий, а интерфейс `UserRepository`: так чище, но проблема не уходит. В доменный код проникла внепроцессная зависимость, и алгоритм больше нельзя проверить без базы или мока. А дальше хуже: в реальной системе рядом с подсчётом скидок появятся блокировки, ретраи, откат транзакции и запись в шину. Обратите внимание на `async`: домен начал ждать сеть.

### Вариант 3: грузим всё заранее {#load-everything}

```python
class User:
    def change_email(self, email: Email, taken: Set[Email]) -> None:
        if email != self._email and email in taken:
            raise EmailTaken(email)
        self._email = email
```

Контроллер загружает все занятые адреса и передаёт их в домен. Сущность сама решает и ни от чего не зависит. Красиво, но на миллионе пользователей бессмысленно. Из зала предложили передавать вместо множества булев флаг `taken`. Но кто его посчитает? Контроллер. И мы вернулись к первому варианту.

### Два из трёх {#two-of-three}

Владимир Хориков называет это [трилеммой DDD](https://enterprisecraftsmanship.com/posts/domain-model-purity-completeness/). У него три свойства: полнота модели (completeness, вся доменная логика в домене), чистота (purity, в домене нет внепроцессных зависимостей) и производительность. На докладе мы называли первые два инкапсуляцией и изоляцией. Получить можно только два из трёх:

| Вариант | Инкапсуляция | Изоляция | Производительность |
|---|---|---|---|
| Проверка в контроллере | нет | да | да |
| Репозиторий в домене | да | нет | да |
| Загрузить всё заранее | да | да | нет |

Порядок жертв, который рекомендует Хориков: если можете позволить себе потерю производительности, жертвуйте ею. Если нет, жертвуйте инкапсуляцией. Изоляцию сохраняйте всегда, потому что изолированная модель тестируема. Честно скажем, что Станислав с этим порядком согласен не до конца: репозиторий в домене ему иногда кажется меньшим злом, чем логика, размазанная по контроллерам. Но аргумент про блокировки и ретраи рядом с бизнес-правилами перевешивает.

### CanExecute / Execute {#can-execute}

Хориков предлагает компромисс, который сохраняет изоляцию и производительность почти без потери инкапсуляции. Это паттерн CanExecute / Execute. Пример у Хорикова другой: email нельзя менять после подтверждения.

```python
class User:
    def can_change_email(self) -> str | None:
        if self._is_email_confirmed:
            return "Email is already confirmed"
        return None

    def change_email(self, email: Email, company: Company) -> None:
        if (reason := self.can_change_email()) is not None:
            raise EmailChangeNotAllowed(reason)
        if email == self._email:
            return
        is_employee = company.is_corporate(email)
        if is_employee != self._is_employee:
            company.change_number_of_employees(1 if is_employee else -1)
        self._email = email
        self._is_employee = is_employee


class UserController:
    async def change_email(self, user_id: UUID, email: Email) -> str:
        user = await self._users.get(user_id)
        if (reason := user.can_change_email()) is not None:
            return reason
        company = await self._companies.get()
        user.change_email(email, company)
        await self._companies.save(company)
        await self._users.save(user)
        return "OK"
```

Контроллер ничего не решает: спрашивает домен, грузит данные и сохраняет. Все решения, включая «можно ли», остаются в `User`. Компанию грузим, только если смена разрешена, так что производительность не страдает.

Проверка внутри `change_email` дублирует `can_change_email` намеренно: вызвать операцию в обход проверки нельзя. В оригинале у Хорикова на этом месте precondition, а на слайдах доклада был `assert`. В Python так делать не стоит: `python -O` выбрасывает все `assert`, и защита исчезнет без единого предупреждения.

У компромисса есть цена. Проверки, которым нужно I/O, вроде уникальности email, всё равно уходят в контроллер. Забытый вызов `can_*` всплывёт только в рантайме. Кода больше: на каждую операцию пара методов. И для CRUD-форм, где пользователю нужно показать все ошибки сразу, паттерн неудобен. Это лучший компромисс, а не решение трилеммы.

### А если запросы придут одновременно {#race}

Из зала прозвучал вопрос, на который мы тогда толком не ответили: что будет, если два человека одновременно попытаются взять один адрес? Ответ неприятный: ни один из трёх вариантов от этого не защищает. Оба запроса проверят, что адрес свободен, оба получат «да», оба сохранят.

Дело в том, что уникальность email относится ко *множеству* пользователей. Сущность `User` отвечает только за себя и не может гарантировать то, что выходит за её границы. Такие правила гарантирует база данных:

```sql
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
```

Домен по-прежнему формулирует правило и проверяет его в нормальном случае, чтобы вернуть пользователю внятную ошибку. А при одновременных запросах правило держит ограничение в базе, и прикладной слой переводит его нарушение в ту же доменную ошибку. Нормализация адреса (регистр, пробелы) живёт в value object `Email`, иначе `Ann@Example.com` и `ann@example.com` пройдут мимо индекса. Как поймать нарушение ограничения внутри транзакции, покажем ниже, когда дойдём до Unit of Work.

## Тактические паттерны {#tactical}

Мы шли от важного к второстепенному, и дальше идёт часть, которую мы считаем наименее важной. Знать все термины ради терминов бессмысленно. Но именно эти слова звучат в холиварах, поэтому пройдёмся по ним.

### Value Object {#value-object}

Value object служит основным строительным блоком. У него нет идентичности: два объекта равны, если равны их значения. Он неизменяем: операции возвращают новый объект. И он всегда валиден: проверка происходит при создании.

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise NegativeMoney(self.amount)

    def __add__(self, other: "Money") -> "Money":
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, qty: int) -> "Money":
        return Money(self.amount * qty, self.currency)

    def __gt__(self, other: "Money") -> bool:
        self._require_same_currency(other)
        return self.amount > other.amount

    def _require_same_currency(self, other: "Money") -> None:
        if other.currency != self.currency:
            raise CurrencyMismatch(self.currency, other.currency)
```

На докладе прозвучала хорошая формулировка: value object похож на тип данных. Есть число 5 и другое число 5, но это одно и то же число. Value object устроен так же, только умнее: у него есть инварианты, и это не просто пятёрка, а положительная пятёрка в рублях. Объекты с одинаковыми значениями взаимозаменяемы, их безопасно передавать куда угодно и легко тестировать. Поэтому максимум логики стоит держать именно в value objects.

Запрет отрицательных сумм здесь решение нашей модели, а не закон природы: в бухгалтерии отрицательные суммы нормальны. То же с самим выбором «value object или сущность». У Эванса есть пример с адресом: интернет-магазину адрес нужен только как значение, по которому отправляют посылку, а для почтовой службы, которая строит маршруты, адрес становится сущностью со своей жизнью. Ответ зависит от контекста.

### Entity {#entity}

У сущности есть идентичность: две сущности равны, если равны их идентификаторы. У неё есть жизненный цикл: состояние меняется, а id остаётся. Сущность сама защищает свои инварианты и меняется только через методы, а сложную логику делегирует value objects.

```python
class Order:
    def __init__(self, order_id: OrderId, currency: Currency) -> None:
        self._id = order_id
        self._status = OrderStatus.NEW
        self._total = Money(Decimal(0), currency)

    @property
    def id(self) -> OrderId:
        return self._id

    def add_item(self, price: Money) -> None:
        if self._status is not OrderStatus.NEW:
            raise OrderIsClosed(self._id)
        self._total = self._total + price  # Money checks the currency and the sign

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
```

`Order` следит за жизненным циклом, `Money` за правилами денег. Два заказа, у которых совпадает всё, кроме id, не взаимозаменяемы. И деталь, специфичная для Python: если определить `__eq__` без `__hash__`, Python выставит `__hash__ = None`, и сущность нельзя будет положить в множество или использовать как ключ словаря.

### Aggregate {#aggregate}

Агрегат объединяет сущности и value objects под одним корнем. Хранится и меняется такая группа только целиком. Обратиться к внутренним объектам можно только через корень, менять их тоже только через него. Если у машины есть колёса, то до колеса не достучаться иначе, чем через интерфейс машины.

```python
class OrderLine:  # an entity inside the aggregate
    def cost(self) -> Money:
        return self.price * self.qty


class Order:  # the aggregate root
    def add_line(self, product_id: ProductId, price: Money, qty: int) -> None:
        line = OrderLine(product_id, price, qty)
        if self.total() + line.cost() > self._limit:
            raise LimitExceeded(self._id)
        self._lines.append(line)

    def total(self) -> Money:
        zero = Money(Decimal(0), self._limit.currency)
        return sum((line.cost() for line in self._lines), zero)

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        return tuple(self._lines)
```

Инвариант «сумма заказа не превышает лимит» затрагивает все строки сразу, поэтому строки и живут внутри агрегата. Читать строки можно, менять напрямую нельзя: инкапсуляция защищает инварианты, а не данные. На другие агрегаты, например на покупателя или товар, заказ ссылается только по id.

Важно, что агрегат существует в модели, а не в базе. В базе никакого «корня» нет: есть родительская таблица `orders` и дочерняя `order_lines`, а `Money` вообще не таблица, а пара колонок в строке.

У агрегата есть правило, которое Вон Вернон формулирует так: граница агрегата совпадает с границей транзакции, одна транзакция меняет один агрегат. Дальше в примерах мы его нарушим: смена email меняет и пользователя, и компанию. В одной базе PostgreSQL это прагматичный выбор, но у него есть цена: агрегаты связываются, растёт конкуренция за блокировки. Если двум агрегатам постоянно нужно меняться вместе, возможно, граница проведена неверно. Если не нужно, второе изменение можно сделать согласованным в конечном счёте через доменное событие.

### Репозитории и фабрики {#repository}

Репозиторий в DDD сохраняет и восстанавливает агрегаты, именно доменные объекты, а не строки и не DTO. Один репозиторий на агрегат: `OrderRepository` есть, `OrderLineRepository` нет. Репозиторий собирает агрегат из строк и раскладывает обратно:

```python
class OrderRepository:
    async def get(self, order_id: OrderId) -> Order:
        order_row = await self._db.fetch_one("orders", id=order_id)
        line_rows = await self._db.fetch_all("order_lines", order_id=order_id)
        return reconstitute_order(order_row, line_rows)

    async def save(self, order: Order) -> None:
        await self._db.upsert("orders", id=order.id, limit=order.limit.amount, currency=order.limit.currency)
        await self._db.delete("order_lines", order_id=order.id)  # lines removed from the aggregate go too
        for line in order.lines:
            await self._db.insert(
                "order_lines",
                id=line.id,
                order_id=order.id,
                product_id=line.product_id,
                price=line.price.amount,
                qty=line.qty,
            )
```

`_db` здесь просто тонкая обёртка над соединением, чтобы не отвлекаться на SQL. В реальном коде эту работу делает ORM.

Фабрика у Эванса создаёт объект атомарно, сразу валидным. Но восстановление из базы не то же самое, что создание. При создании нарушенный инвариант означает ошибку ввода, и фабрика просто отказывается создавать объект. При восстановлении объект уже существует, и нарушенный инвариант означает испорченные данные: реагировать нужно иначе, но и делать вид, что всё в порядке, нельзя.

И последнее правило из той же главы Эванса: транзакцией управляет клиент, а не репозиторий. Репозиторий не коммитит. Почему это важно и что ломается иначе, мы подробно разбирали в [статье про сессии и транзакции SQLAlchemy](2026-10-08-sqlalchemy-sessions-and-transactions.md).

### Нужен ли репозиторию интерфейс {#abstract-repository}

Чистая архитектура Роберта Мартина отвечает «да»: домен объявляет интерфейс, инфраструктура его реализует, зависимости направлены внутрь, база становится деталью, а бизнес-правила можно тестировать без неё.

Хориков отвечает иначе. Реализация репозитория одна, и интерфейс нужен только ради моков. Но своя база относится к управляемым зависимостям: её не мокают, а проверяют интеграционными тестами. Моки не нужны, значит, и интерфейс не нужен. Абстракции открывают, а не изобретают: появится вторая реализация, тогда и выделим интерфейс. Авторы «Architecture Patterns with Python» занимают третью позицию: абстрактный репозиторий плюс in-memory `FakeRepository`, на котором быстро тестируется сервисный слой.

Нам ближе такой синтез. Если домен чистый, как в разделе про функциональное ядро, репозитории вызывает только прикладной слой, и главный аргумент чистой архитектуры, «домен не должен зависеть от базы», снимается сам собой: домен от репозиториев и так не зависит. Интерфейс оправдан, когда вторая реализация действительно появилась. На докладе как раз вспомнили такой случай: кеширующий репозиторий-декоратор поверх обычного с тем же протоколом. К тому же в Python `Protocol` дешёв: реализации не нужно от него наследоваться, так что лишняя абстракция обходится недорого.

### Чтения мимо агрегатов {#reads}

Ещё один вопрос из зала: если репозиторий возвращает только агрегаты, как быть с чтениями, где нужны джойны пяти таблиц и пагинация? Собирать ради списка заказов полные агрегаты дорого и бессмысленно.

Не надо. Агрегаты нужны, чтобы *менять* состояние, сохраняя инварианты. Чтение ничего не меняет, поэтому запрос может идти мимо модели прямо в SQL и возвращать плоскую структуру под экран. Это облегчённый CQRS: команды через агрегаты, запросы отдельно.

Попутно развеем популярное заблуждение. На докладе прозвучало, что по Фаулеру DTO считается антипаттерном. Это не так: Data Transfer Object описан в самой книге Фаулера как паттерн для передачи данных между процессами. Критикует он [LocalDTO](https://martinfowler.com/bliki/LocalDTO.html), то есть DTO внутри одного процесса, где они плодят код и толкают к анемичной модели. Объявлять злом любые DTO предлагает Егор Бугаенко. Компромисс простой: DTO на границах (API, очередь, ответ запроса на чтение), поведение внутри модели.

### Unit of Work {#unit-of-work}

Допустим, у каждого репозитория своё соединение. Тогда смена email может закончиться так: компания сохранилась, а пользователь нет. Нужна общая транзакция, и тут появляется Unit of Work. Фаулер определяет его так: он ведёт список объектов, затронутых бизнес-транзакцией, и координирует запись изменений и разрешение проблем параллельного доступа. То есть копит изменения и пишет их в конце одним пакетом: транзакция короче, блокировок и запросов меньше.

Unit of Work, строго говоря, не паттерн DDD, а паттерн хранения данных из каталога Фаулера. DDD лишь опирается на него. В Python его почти никто не пишет сам: [`Session` в SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) уже реализует Unit of Work вместе с identity map: она сама отслеживает изменённые объекты и пишет их при коммите.

Остаётся решить, кто владеет транзакцией и как прикладной код получает репозитории. В DDD-коде обычно пишут `uow.orders.add(order)`: репозитории живут внутри Unit of Work. В [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/) это `AsyncSQLAlchemyUnitOfWork`: каждый `transaction()` открывает свою сессию, коммитит при нормальном выходе и откатывает при исключении, а объект транзакции отдаёт репозитории одного ограниченного контекста:

```python
from sqlalchemy_foundation_kit.uow import AsyncSQLAlchemyUnitOfWork, AsyncSQLAlchemyUowTransaction


class IdentityTransaction(AsyncSQLAlchemyUowTransaction):
    """Repositories of the identity context in one transaction."""

    @property
    def users(self) -> UserRepository:
        return UserRepository(self.session)

    @property
    def companies(self) -> CompanyRepository:
        return CompanyRepository(self.session)


uow = AsyncSQLAlchemyUnitOfWork(session_factory, IdentityTransaction)
```

Для гонки из раздела про трилемму важно, где всплывёт нарушение `uq_users_email`. Если репозиторий выполняет UPDATE сразу, ошибка вылетит прямо из `save()`. Если изменения ждут в сессии, их отправит `flush()`, который `transaction()` по умолчанию делает перед коммитом. В обоих случаях из `transaction()` выходит `IntegrityError`, и его можно перевести в доменную ошибку. Соберём это вместе с доменными событиями.

### Domain Events {#domain-events}

Последний тактический паттерн нужен, чтобы убрать из домена ещё одну внепроцессную зависимость. Допустим, после смены email сервис должен отправить сообщение в шину. Можно отправить его прямо из `User.change_email`, но тогда в домене появляется шина, а с ней I/O, ретраи и всё, от чего мы уходили в трилемме.

Вместо этого сущность фиксирует, что произошло, и больше ничего не делает:

```python
@dataclass(frozen=True)
class EmailChanged:
    user_id: UUID
    email: Email


class User:
    def change_email(self, email: Email, company: Company) -> None:
        ...  # checks and the email change, as above
        self._events.append(EmailChanged(self.id, email))

    def pull_events(self) -> list[EmailChanged]:
        events, self._events = self._events, []
        return events
```

Решение в домене, отправка снаружи: пользователь даже не знает, что где-то есть шина. В оригинальной книге Эванса 2003 года доменных событий, кстати, нет. Их добавили позже: Вернон в красной книге и сам Эванс в DDD Reference.

Отправлять события после коммита ненадёжно, и на докладе мы честно попросили зал не придираться. Упадёт процесс между коммитом и отправкой, и событие потеряно. Отправите до коммита, а транзакция откатится, и мир узнает о смене email, которой не было. Надёжный вариант называется transactional outbox: событие записывается строкой в той же транзакции, что и изменения агрегата, а отдельный процесс публикует такие строки в брокер. Подробно эту схему мы разбирали в [статье про Outbox и Inbox](2026-10-03-reliable-events-outbox-inbox-kafka.md). В [omni-box](https://bedrock-python.github.io/omni-box/) у события outbox даже поля называются на языке DDD: `aggregate_type` и `aggregate_id`.

Добавим outbox в объект транзакции и соберём всю операцию:

```python
from omni_box import OmniBoxDomainService, OutboxEvent
from omni_box.infra.storage.postgres import PostgresOutboxRepository
from sqlalchemy.exc import IntegrityError


class IdentityTransaction(AsyncSQLAlchemyUowTransaction):
    ...  # users and companies, as above

    @property
    def outbox(self) -> PostgresOutboxRepository:
        return PostgresOutboxRepository(self.session, model_class=OutboxEventDB)


def to_outbox(event: EmailChanged) -> OutboxEvent:
    return OmniBoxDomainService().create_outbox_event(
        aggregate_type="user",
        aggregate_id=event.user_id,
        event_type="user.email_changed",
        topic="users.email-changed",
        partition_key=str(event.user_id),
        payload={"user_id": event.user_id, "email": str(event.email)},
    )


async def change_email(uow: AsyncSQLAlchemyUnitOfWork[IdentityTransaction], user_id: UUID, email: Email) -> str:
    try:
        async with uow.transaction() as tx:
            user = await tx.users.get(user_id)
            if (reason := user.can_change_email()) is not None:
                return reason
            company = await tx.companies.get()
            user.change_email(email, company)
            await tx.users.save(user)
            await tx.companies.save(company)
            for event in user.pull_events():
                await tx.outbox.create(to_outbox(event))
    except IntegrityError as exc:
        if not is_unique_violation(exc, "uq_users_email"):
            raise
        return "Email is taken"
    return "OK"
```

`is_unique_violation` проверяет SQLSTATE `23505` и имя ограничения; реализация для asyncpg лежит в [практикуме](../lab/2026-11-02-domain-driven-design/README.md). Пользователь, компания и событие сохраняются вместе или не сохраняются вовсе. Ограничение здесь и есть проверка: занят ли адрес давно или параллельный запрос успел на миллисекунду раньше, пользователь получит одну и ту же ошибку. Практикум воспроизводит гонку: две транзакции читают адрес как свободный, а закоммитить удаётся только одной. В самой функции нет ни одного бизнес-решения: она грузит, спрашивает домен, сохраняет.

### Доменный и прикладной слой {#domain-vs-application}

Основная часть доклада закончилась вопросом: чем доменный слой отличается от прикладного? Доменный слой отвечает на вопрос «как»: как перевести деньги, как сменить email. Прикладной отвечает на вопрос «что мы хотим сделать»: это простой, почти тупой сценарий, который грузит сложные объекты, вызывает их методы и сохраняет. Функция `change_email` выше относится к прикладному слою.

```python
def transfer(source: Account, target: Account, amount: Money) -> None:
    if source.currency != target.currency:
        raise CurrencyMismatch(source.currency, target.currency)
    source.withdraw(amount)
    target.deposit(amount)
```

Перевод между счетами затрагивает два объекта и не принадлежит ни одному из них. У Эванса такая операция называется domain service, в чистой архитектуре прикладной сценарий называют use case, в других местах handler или application service. Названия не важны, важен слой: решения в домене, координация в прикладном.

### Спецификация {#specification}

На докладе этот паттерн пропустили как скучный, но из зала попросили рассказать о нём хотя бы вкратце. Бывает, что бизнес-правило не помещается в одну сущность: оно комбинирует условия, использует чужие понятия, а ещё по нему нужно искать в базе. Тогда правило становится отдельным value object. Классический пример Эванса: просроченный счёт с учётом отсрочки клиента.

```python
@dataclass(frozen=True)
class DelinquentInvoice:
    today: date

    def is_satisfied_by(self, invoice: Invoice) -> bool:
        return self.today > invoice.due_date + invoice.customer.payment_grace_period
```

Одна и та же спецификация проверяет объект в памяти, а если перевести её в условие запроса, выбирает подходящие строки из базы. Спецификации можно комбинировать через «и», «или», «не». Смысл в том, что у правила одно место, и проверка не расходится с поиском. В Python это часто перебор: пока правило зависит только от полей сущности, хватает метода `invoice.is_overdue(today)`.

## DDD и тесты {#testing}

Тестирование мы обещали в начале, и оно, пожалуй, лучше всего показывает, зачем вся эта возня с изоляцией. Хориков делит код по двум осям: насколько он сложен или важен для предметной области и сколько у него коллабораторов.

| | Мало коллабораторов | Много коллабораторов |
|---|---|---|
| **Сложный или важный** | доменная модель и алгоритмы: юнит-тесты | переусложнённый код: рефакторить |
| **Простой** | тривиальный код (DTO, геттеры): не тестировать | контроллеры: интеграционные тесты |

Доменная модель покрывается юнит-тестами целиком и без единого мока: в ней нечего мокать. Контроллеры проверяются интеграционными тестами, и только в них появляются моки. Переусложнённый код, который одновременно решает и координирует, нужно разнести по двум другим клеткам. Тест с `AuditManager` выше как раз из левого верхнего квадрата.

На докладе задали резонный вопрос: зачем тестировать домен отдельно, если сценарии контроллера и так через него проходят? Интеграционный тест действительно покрывает больше и показательнее. Но его дороже писать: он требует много подготовки. Им трудно попасть в каждую ветку: чтобы добраться до каждого `if`, данные приходится подбирать изощрённо. Он медленный, потому что работает с базой. И его сложнее поддерживать. Если бы интеграционные тесты выполнялись мгновенно и писались бесплатно, можно было бы писать только их. Многие команды, и наша тоже, по сути так и живут, но классическая позиция в том, что быстрые юнит-тесты на домен дают лучшую обратную связь.

### Что мокать {#what-to-mock}

| Зависимость | Пример | Что делаем |
|---|---|---|
| Внутрипроцессная | домен, value objects, сущности | настоящие объекты, не мокаем |
| Управляемая | своя база, видна только нашему сервису | настоящая база в интеграционных тестах |
| Неуправляемая | шина, SMTP, чужой API, видны другим системам | мок: это наблюдаемое поведение |

Мок базы проверяет, *как* мы пишем, а не *что* получилось, и ломается при любом рефакторинге. Неуправляемые зависимости мокаем на самом краю системы, на последнем типе перед сетью:

```python
class Bus(Protocol):  # the only interface: the last type before the network
    def send(self, message: str) -> None: ...


class MessageBus:
    def __init__(self, bus: Bus) -> None:
        self._bus = bus

    def send_email_changed(self, user_id: UUID, email: Email) -> None:
        self._bus.send(f"Type: USER EMAIL CHANGED; Id: {user_id}; NewEmail: {email}")
```

Тест мокает `Bus`, а не `MessageBus`, и проверяет ровно ту строку, которая уйдёт в сеть. С outbox картина ещё проще: сообщение сначала становится строкой в нашей собственной базе, и интеграционный тест проверяет эту строку. Мок брокера нужен только в тестах публикатора.

### Публичный API {#public-api}

Тестируем наблюдаемое поведение, а не детали реализации. Приватные методы проверяются через публичные. Если хочется протестировать приватный метод или запатчить что-то внутри класса, это сигнал о дизайне: скорее всего, там спрятан отдельный объект, которому не хватает имени. И чем выше уровень объекта, тем больше его API должен быть похож на язык предметной области: публичный API агрегата и есть его контракт на едином языке.

## Когда DDD не нужен {#when-not-to-use}

Последний вопрос из зала был самым честным: зачем всё это, если можно разложить код по трём папкам, `core`, `infra` и `use_cases`, и жить без лишних сущностей?

Часто и не нужно. DDD окупается, когда предметная область сложная и вы сами её до конца не понимаете. Когда заказчик не вы. Когда вокруг много людей и каждый знает свой кусок. Когда ошибиться нельзя: если вы начисляете людям кредиты, нужно точно знать, по какому правилу и где оно записано. Сложность здесь в логике, а не в нагрузке: высокий RPS к DDD отношения не имеет. Если сервис перекладывает данные из Kafka в PostgreSQL, модель ему не нужна, и transaction script будет честнее.

Зачем вообще паттерны? У Фаулера есть [гипотеза о выносливости дизайна](https://martinfowler.com/bliki/DesignStaminaHypothesis.html): без дизайна вы сначала быстрее, но со временем каждая фича даётся всё дороже, и в какой-то момент вас обгоняет тот, кто вложился в структуру. Жадные правки на месте дают быстрый старт, а потом каждое изменение ломает соседние, тесты падают от рефакторинга, и перед релизом никто не уверен, что система работает. Хорошая модель даёт обратное: новое поведение добавляется рядом, а не поперёк. Когда нам понадобилось подключить ещё одного провайдера в одном из наших сервисов, это свелось к новой реализации интерфейса: остальной код не поменялся.

И мысль, которую мы вынесли из подготовки доклада. С ИИ-агентами в разработке стратегические идеи DDD, похоже, становятся важнее, а тактические теряют вес. Агенту, как и новому человеку в команде, нужны словарь и границы: какие понятия есть в системе, что они значат в этом контексте и какие правила нельзя нарушать. Код по паттернам агент напишет и сам, а модель за вас не придумает. Как мы готовим для агентов такой контекст, рассказывали в [статье о документации для ИИ-агентов](2026-10-26-documentation-for-ai-coding-agents.md).

## Что почитать {#sources}

- Эрик Эванс, «Предметно-ориентированное проектирование (DDD)», в оригинале *Domain-Driven Design* (2003). Синяя книга, с неё всё началось. Обновлённая выжимка паттернов: [*Domain-Driven Design Reference*](https://www.domainlanguage.com/ddd/reference/) (2015).
- Вон Вернон, «Реализация методов предметно-ориентированного проектирования», в оригинале *Implementing Domain-Driven Design* (2013). Красная книга, практичнее синей.
- Владимир Хориков, «Принципы юнит-тестирования», в оригинале *Unit Testing Principles, Practices, and Patterns* (2020). Половина книги на самом деле про то, как устроить доменную модель. Отсюда квадранты, управляемые зависимости и CanExecute / Execute.
- Влад Хононов, *Learning Domain-Driven Design* (2021). Лучшее, что мы знаем, про субдомены и про то, сколько DDD тратить на каждый.
- Гарри Персиваль и Боб Грегори, [*Architecture Patterns with Python*](https://www.cosmicpython.com/) (2020). Репозитории, Unit of Work, агрегаты и события на Python и SQLAlchemy.
- Мартин Фаулер, *Patterns of Enterprise Application Architecture* (2002): Unit of Work, Transaction Script, Data Transfer Object.
