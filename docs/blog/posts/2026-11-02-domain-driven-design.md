---
date: 2026-11-02
authors:
  - stas
  - alex
author: Stanislav Shimovolos, Alex Shalaev
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

# Domain-Driven Design: the model first, the patterns later {#domain-driven-design}

<p class="bdr-post__byline"><a href="https://github.com/stanislaushimovolos">Stanislav Shimovolos</a> and <a href="https://github.com/AlexeyShalaev">Alex Shalaev</a></p>

<div class="bdr-post__hero" data-bdr-post="2026-11-02-domain-driven-design" role="img" aria-label="Separate contexts keep their own models, and everything connects to one core model at the center" markdown="0"></div>

Every serious service has rules that developers did not invent: when a customer gets a discount, who counts as an employee, how much cargo a ship may take over its limit.

While there are a dozen such rules, people keep them in their heads and in a couple of `if` statements. Once there are hundreds and the business changes them every quarter, code without a shared picture starts to fight back: a fix in one place breaks three others, and in meetings developers and domain experts talk past each other. Domain-Driven Design, or DDD, is a set of principles for exactly these services. Their difficulty lies not in the load but in the domain itself, and the code is built around a model of that domain rather than around tables and endpoints.

This article grew out of an internal talk for backend developers, ML engineers and analysts. The questions from the audience turned out to be as useful as the slides, and many of them made it into the text.

DDD ideas are usually split into two levels. Strategic ideas answer what to model and where: what model and language the system has, where the context boundaries run, which parts matter to the business and where to invest effort. Tactical ideas answer how to express the model in code within one context: value objects, entities, aggregates, repositories, domain events. Evans covers tactics in the second part of his book and strategy only in the last, fourth part, and tactics are what people usually argue about. This article goes in the opposite order: strategy first (the model, the language, boundaries, subdomains), then the principles that connect it to code (invariants and the trilemma), and tactics at the end.

Two caveats up front. This is neither an expert's view nor a retelling of the blue book, but an overview of the key ideas with a subjective assessment. DDD is also one of the most hotly debated topics in software: almost every claim here has respected opponents, and where it does, they are named. The examples need Python 3.12 or newer. The code in this article is checked by a [lab](../lab/2026-11-02-domain-driven-design/README.md) on Python 3.13, SQLAlchemy 2.1.6, sqlalchemy-foundation-kit 0.5.1, omni-box 0.3.1 and PostgreSQL 17.11.

<!-- more -->

## The model matters more than the code {#model}

If you keep only one idea from DDD, keep this one: before you write a feature, fit it into the model. The talk rated this idea at 95% of DDD and 95% of success. The number is subjective, but this is where to start.

The usual way to solve a task is direct: a requirement arrives, you find a place in the code, you add to it. DDD puts one more step between the requirement and the code. First you sit down and work out which entities the process has, what happens to them and how they interact. On paper, on a whiteboard, in your head, it does not matter where. The picture you end up with is the domain model: an idea of how this piece of the world works.

Physics offers a good analogy. The atom is complicated, and physicists describe it with models: in Rutherford's, electrons orbit the nucleus like planets; then quantum mechanics arrived. No model is "the truth", but each one is useful and each next one is more accurate. Software works the same way: a model does not have to match reality, it has to be a useful simplification.

Once there is a model, features are built inside it. You cannot just add an `if` or prop something up with a workaround when it does not fit your entities. First you adapt the model to the new requirement, then you write the code. Sometimes the code drifts away from reality, and then the model is refined again. Evans calls this refactoring toward deeper insight.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>The model-driven design loop</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="0" data-search-exclude>
<svg class="bdr-svg" viewBox="0 0 440 424" role="img" aria-labelledby="ddd-cycle-title ddd-cycle-desc" xmlns="http://www.w3.org/2000/svg">
<title id="ddd-cycle-title">The model-driven design loop</title>
<desc id="ddd-cycle-desc">Expert knowledge is distilled into a model, the model is expressed directly in code, and a mismatch between code and reality sends the team back to the experts and the model.</desc>
<defs>
<marker id="ddd-cycle-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head" d="M0,0 L10,5 L0,10 z"/></marker>
<marker id="ddd-cycle-head-accent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head bdr-svg__head--accent" d="M0,0 L10,5 L0,10 z"/></marker>
</defs>
<g class="bdr-svg__box"><rect x="170" y="20" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="45" text-anchor="middle">Domain</text><text class="bdr-svg__sub" x="295" y="64" text-anchor="middle">experts and the real world</text></g>
<g class="bdr-svg__box"><rect x="170" y="130" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="155" text-anchor="middle">Knowledge crunching</text><text class="bdr-svg__sub" x="295" y="174" text-anchor="middle">learning from the experts</text></g>
<g class="bdr-svg__box bdr-svg__box--strong"><rect x="170" y="240" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="265" text-anchor="middle">Model</text><text class="bdr-svg__sub" x="295" y="284" text-anchor="middle">a useful simplification</text></g>
<g class="bdr-svg__box"><rect x="170" y="350" width="250" height="58" rx="10"/><text class="bdr-svg__name" x="295" y="375" text-anchor="middle">Code</text><text class="bdr-svg__sub" x="295" y="394" text-anchor="middle">the model, expressed directly</text></g>
<path class="bdr-svg__edge" d="M295 78 V127" marker-end="url(#ddd-cycle-head)"/>
<text class="bdr-svg__note" x="306" y="108">talking to experts</text>
<path class="bdr-svg__edge" d="M295 188 V237" marker-end="url(#ddd-cycle-head)"/>
<text class="bdr-svg__note" x="306" y="218">distillation</text>
<path class="bdr-svg__edge" d="M295 298 V347" marker-end="url(#ddd-cycle-head)"/>
<text class="bdr-svg__note" x="306" y="328">translation into code</text>
<path class="bdr-svg__edge bdr-svg__edge--accent bdr-svg__edge--dashed" d="M170 379 H44 V49 H167" marker-end="url(#ddd-cycle-head-accent)"/>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="182">mismatch</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="199">with reality:</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="216">refactoring</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="233">toward deeper</text>
<text class="bdr-svg__note bdr-svg__note--accent" x="56" y="250">insight</text>
</svg>
</div>
<p class="bdr-diagram__caption">Expert knowledge is distilled into a model, the model is expressed directly in code, and a mismatch between code and reality sends the team back to the experts and the model.</p>
</figure>
<!-- /diagram:concept -->

The worst thing you can do in this loop is break the model. And the most valuable thing in a project is not the code but the model: how the team understands the problem. Code matters, but it is only a record of the model. That sounds abstract, yet in practice it is the difference between "moving JSON from one endpoint to another" and "solving this particular problem with these particular concepts". Many services have no model at all: things get bolted on here and there, and nobody can say which rules the system must never break.

## Ubiquitous language {#ubiquitous-language}

Second in importance after the model, worth another 4% of success, is the ubiquitous language.

Picture a service for doctors. The doctors speak in their terms, the developers in theirs, and at every meeting both sides nod politely without understanding each other. The doctors ask for one thing, the developers build another, and a couple of months later it turns out that everyone meant something different by the same word.

A typical chain of translations looks like this. The expert says "the shopper places an order", the analyst writes "the user creates a request" in the ticket, and the code gets `session.add(order_row)`. Each translation loses part of the meaning, and a year later the analyst's "request" has grown properties that the expert's "order" never had.

The cure is one language, defined by the model. If the model has "order", "shipment" and "payment", those words are used in meetings, in tickets, and in the names of classes, methods and tests. If the team agreed to say `customer`, nobody writes `user`: otherwise the two words start living separate lives. The language is alive: as soon as you notice a mismatch, you fix the language and the model together and make sure everyone hears about it.

A language has limits to where it applies, and that is the next idea.

## Bounded Context: where a model ends {#bounded-context}

A large domain is hard to describe with a single model. Take an online shop with a catalog, a warehouse and billing. Each of them has a "product", but these are three different products. For the catalog it is a description, photos and specifications; for the warehouse, stock levels, a bin location and a weight; for billing, a price, taxes and discounts. Merging them into one `Product` class produces a monster that all three teams are afraid to touch.

DDD suggests something else: parts of the domain (subdomains) map onto bounded contexts. A bounded context is the boundary inside which one model, with its own language, applies. Inside the warehouse context, "product" means exactly one thing. Contexts are isolated from each other and talk by explicit rules.

This is a logical division, not a deployment decision. A monolith with three modules or three microservices makes no difference to DDD: what matters is that each context has its own model. Ideally one subdomain maps onto one context, but in real life the mapping is not always one to one.

How contexts relate to each other is described by a context map. Evans gives a whole set of relationships for it:

| Relationship | What happens |
|---|---|
| Shared Kernel | two teams share a small common part of the model and change it only together |
| Customer / Supplier | the supplier (upstream) takes the needs of the consumer (downstream) into its plans |
| Conformist | the consumer adopts the supplier's model as is, without translation |
| Anticorruption Layer | the consumer translates the foreign model into its own through a layer of adapters and does not depend on it |
| Open Host Service, Published Language | the supplier publishes a protocol and a format for many consumers at once |
| Separate Ways | the contexts do not integrate at all |

In practice the two you meet most often are opposite approaches: an Anticorruption Layer, when a context protects its model from a foreign one, and Conformist, when a context admits it is less important and simply lives in someone else's concepts.

Martin Fowler has a well-known [illustration](https://martinfowler.com/bliki/BoundedContext.html): a sales context and a support context, both with a customer and a product. The entities look the same, but each context has its own view of them and its own attributes. Fowler does not suggest merging them: each context has its own model of the shared concept, and integrating them requires a mapping. So duplication, both in code and in the database, is fine. What matters more is loose coupling between contexts and high cohesion within each one.

The talk gave bounded contexts "another half a percent of success" after the model and the language. To be fair, Vernon and Khononov put them at the center of strategic DDD, and as soon as one word gets two meanings or two teams work on the same system, it is hard to disagree with them.

## Core, supporting, generic: where to spend effort {#subdomains}

Contexts divide a system by meaning. There is a second division too: by importance to the business. Subdomains come in three types.

The **core subdomain** is what sets the company apart from its competitors; it is the reason the company exists. Take a food delivery service. Its core is courier dispatching, delivery time estimates and dynamic pricing. The dispatching algorithm itself, that is, not the way a push notification reaches the courier.

The core needs real modeling, and in the long run you build it yourself. If an off-the-shelf product covered your core entirely, your own product would be pointless. If it covers the core partly, the workarounds begin. Try building food delivery on a task tracker like Notion: it has cards and statuses too, but an order is not a ticket. There is plenty you do not need (sprints, story points) and nothing you do: the courier's location, the delivery window, a route through several orders. All of that has to be bolted on with custom fields and scripts. Evans advises putting the team's best people on the core. It is a good reason to ask yourself honestly who is writing your dispatching code right now.

That does not mean the core is written without frameworks. A web framework and an ORM around the core are perfectly fine. The problem starts when the core model is bent to fit someone else's product or framework.

A **supporting subdomain** is necessary and specific to the business, but not unique. For delivery that means the restaurant catalog, the restaurant dashboard and reviews. Things go badly without them, but they are not where the competitive edge is. A simple test from the discussion at the talk: keep only the core and the product still makes sense; keep only the supporting parts and it is useless.

A **generic subdomain** covers standard problems that were solved long ago and that everyone has: payments, authentication, notifications. Nobody reinvents them: you take an existing solution, service or library.

Where the line falls depends on the business. Notifications to couriers stay generic as long as your edge is not delivering them faster and smarter than anyone else. If it is, notifications become core. The classification also works outside the backend: the ML engineers in the audience sorted their own work in no time. The model pipeline went into core; saving weights in safetensors and the distributed training framework went into generic; and preparing data from a dozen formats, which you end up writing yourself for each project anyway, went into supporting.

The main practical conclusion follows from this classification: how much DDD to spend on each part. Khononov, in "Learning Domain-Driven Design", ties the subdomain type directly to the way you write its logic. A rich domain model and the full set of DDD tactics pay off in the core. For supporting subdomains, plain CRUD or a transaction script is often enough. Generic ones are bought and hidden behind an adapter. Applying DDD everywhere in the same way is a reliable way to end up hating it.

Someone in the audience also asked how this division relates to the domain, application and infrastructure layers. Subdomains cut the system by importance; layers cut each part by responsibility. The two axes are orthogonal: each context can have its own layers, and there is no contradiction. What is more, each subdomain gets its own set of layers. The core has a rich domain model at the center. A supporting subdomain often gets by with an API and a transaction script over tables. And a generic one is someone else's service altogether, so all that is left of it in the code is an adapter.

<!-- diagram:layers -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>Layers inside subdomains</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="0" data-search-exclude>
<svg class="bdr-svg" viewBox="0 0 440 636" role="img" aria-labelledby="ddd-layers-title ddd-layers-desc" xmlns="http://www.w3.org/2000/svg">
<title id="ddd-layers-title">Layers inside subdomains</title>
<desc id="ddd-layers-desc">In core, the application layer and infrastructure depend on the domain model at the center, supporting has two layers and no domain model, and generic stays an off-the-shelf service that core reaches through an adapter.</desc>
<defs>
<marker id="ddd-layers-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="bdr-svg__head" d="M0,0 L10,5 L0,10 z"/></marker>
<marker id="ddd-layers-hollow" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9" markerHeight="9" orient="auto"><path class="bdr-svg__head bdr-svg__head--hollow" d="M1,1 L11,6 L1,11 z"/></marker>
</defs>
<g class="bdr-svg__panel"><rect x="16" y="16" width="408" height="252" rx="12"/></g>
<text class="bdr-svg__title" x="36" y="44">Core: dispatching</text>
<text class="bdr-svg__sub" x="36" y="63">rich model, all of tactical DDD</text>
<g class="bdr-svg__box"><rect x="36" y="78" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="97">Application</text><text class="bdr-svg__sub" x="52" y="114">the “assign a courier” use case</text></g>
<path class="bdr-svg__edge" d="M220 124 V143" marker-end="url(#ddd-layers-head)"/>
<text class="bdr-svg__note" x="232" y="138">calls</text>
<g class="bdr-svg__box bdr-svg__box--accent"><rect x="36" y="146" width="368" height="46" rx="8"/><text class="bdr-svg__name bdr-svg__name--accent" x="52" y="165">Domain</text><text class="bdr-svg__sub" x="52" y="182"><tspan class="bdr-svg__code">Order</tspan>, <tspan class="bdr-svg__code">Courier</tspan>, assignment policy</text></g>
<path class="bdr-svg__edge bdr-svg__edge--dashed" d="M220 214 V195" marker-end="url(#ddd-layers-hollow)"/>
<text class="bdr-svg__note" x="232" y="208">implements interfaces</text>
<g class="bdr-svg__box"><rect x="36" y="214" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="233">Infrastructure</text><text class="bdr-svg__sub" x="52" y="250">repositories and adapters</text></g>
<g class="bdr-svg__panel"><rect x="16" y="292" width="408" height="184" rx="12"/></g>
<text class="bdr-svg__title" x="36" y="320">Supporting: restaurant catalog</text>
<text class="bdr-svg__sub" x="36" y="339">CRUD without tactical DDD</text>
<g class="bdr-svg__box"><rect x="36" y="354" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="373">API</text><text class="bdr-svg__sub" x="52" y="390">restaurant dashboard endpoints</text></g>
<path class="bdr-svg__edge" d="M220 400 V419" marker-end="url(#ddd-layers-head)"/>
<g class="bdr-svg__box"><rect x="36" y="422" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="441">Transaction script</text><text class="bdr-svg__sub" x="52" y="458">SQL over tables, no domain model</text></g>
<g class="bdr-svg__panel"><rect x="16" y="500" width="408" height="120" rx="12"/></g>
<text class="bdr-svg__title" x="36" y="528">Generic: payments</text>
<text class="bdr-svg__sub" x="36" y="547">bought, not built</text>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="36" y="562" width="368" height="46" rx="8"/><text class="bdr-svg__name" x="52" y="581">Off-the-shelf payment service</text><text class="bdr-svg__sub" x="52" y="598">all we keep is an adapter in core infrastructure</text></g>
</svg>
</div>
<p class="bdr-diagram__caption">In core, the application layer and infrastructure depend on the domain model at the center, supporting has two layers and no domain model, and generic stays an off-the-shelf service that core reaches through an adapter.</p>
</figure>
<!-- /diagram:layers -->

## Dependencies point at the core {#dependencies}

Here is what this looks like in code. The core depends on nothing. It needs payments and SMS, so it declares the `PaymentGateway` and `Notifier` interfaces in its own language, and adapters in the infrastructure implement them on top of a specific vendor. When the payment provider changes, only the adapter is rewritten. This is the Anticorruption Layer from the table above, assembled through dependency inversion.

The supporting context (the restaurant catalog) feeds the core data and events. So that the core does not depend on the catalog's model, the core defines the contract and the catalog fulfills it. The result is Customer / Supplier with the core, as the consumer, deciding what it needs.

<!-- diagram:dependencies -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>Dependencies point at the core</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="0" data-search-exclude>
<svg class="bdr-svg" viewBox="0 0 440 604" role="img" aria-labelledby="ddd-deps-title ddd-deps-desc" xmlns="http://www.w3.org/2000/svg">
<title id="ddd-deps-title">Dependencies point at the core</title>
<desc id="ddd-deps-desc">Core declares the PaymentGateway and Notifier interfaces, adapters implement them on top of the payment service and the SMS gateway, and the restaurant catalog feeds core data under a contract that core defines.</desc>
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
<g class="bdr-svg__box"><rect x="70" y="16" width="300" height="58" rx="10"/><text class="bdr-svg__name" x="220" y="41" text-anchor="middle">Supporting: restaurant catalog</text><text class="bdr-svg__sub" x="220" y="60" text-anchor="middle">CRUD without tactical DDD</text></g>
<text class="bdr-svg__note" x="232" y="96">data and events under</text>
<text class="bdr-svg__note" x="232" y="112">a contract core defines</text>
<text class="bdr-svg__title bdr-svg__title--accent" x="36" y="156">Core: dispatching</text>
<text class="bdr-svg__sub" x="36" y="175">rich domain model</text>
<g class="bdr-svg__box"><rect x="36" y="188" width="112" height="34" rx="17"/><text class="bdr-svg__code" x="92" y="210" text-anchor="middle">Order</text></g>
<g class="bdr-svg__box"><rect x="164" y="188" width="112" height="34" rx="17"/><text class="bdr-svg__code" x="220" y="210" text-anchor="middle">Courier</text></g>
<g class="bdr-svg__box"><rect x="292" y="188" width="112" height="34" rx="17"/><text class="bdr-svg__code" x="348" y="210" text-anchor="middle">Restaurant</text></g>
<text class="bdr-svg__note" x="36" y="246">interfaces that core declares</text>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="36" y="256" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="124" y="283" text-anchor="middle">PaymentGateway</text></g>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="228" y="256" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="316" y="283" text-anchor="middle">Notifier</text></g>
<text class="bdr-svg__note" x="220" y="342" text-anchor="middle">implement</text>
<text class="bdr-svg__sub bdr-svg__halo" x="36" y="384">Anticorruption Layer in infrastructure</text>
<g class="bdr-svg__box"><rect x="36" y="396" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="124" y="423" text-anchor="middle">PaymentAdapter</text></g>
<g class="bdr-svg__box"><rect x="228" y="396" width="176" height="44" rx="8"/><text class="bdr-svg__code" x="316" y="423" text-anchor="middle">SmsAdapter</text></g>
<text class="bdr-svg__note" x="220" y="478" text-anchor="middle">call</text>
<text class="bdr-svg__sub bdr-svg__halo" x="36" y="512">Generic: off-the-shelf services</text>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="36" y="524" width="176" height="44" rx="8"/><text class="bdr-svg__name" x="124" y="551" text-anchor="middle">Payment service</text></g>
<g class="bdr-svg__box bdr-svg__box--dashed"><rect x="228" y="524" width="176" height="44" rx="8"/><text class="bdr-svg__name" x="316" y="551" text-anchor="middle">SMS gateway</text></g>
</svg>
</div>
<p class="bdr-diagram__caption">Core declares the PaymentGateway and Notifier interfaces, adapters implement them on top of the payment service and the SMS gateway, and the restaurant catalog feeds core data under a contract that core defines.</p>
</figure>
<!-- /diagram:dependencies -->

This is where DDD meets clean, onion and hexagonal architectures. DDD says *what* to isolate: the domain model. These architectures say *how*: dependencies point inward, toward the model, and the database and UI become details. Interestingly, Evans himself in 2003 used a classic layered architecture in which the domain sits above the infrastructure and depends on it. Dependencies were inverted later: Alistair Cockburn's hexagonal architecture (2005), Jeffrey Palermo's onion (2008), Robert Martin's clean architecture (2012). Evans's requirement to isolate the domain stayed; the means got better.

## Rich model and anemic model {#rich-model}

From here on it is about code, and the discussion gets more pedantic.

What is a model from the code's point of view? A set of objects that maintain invariants: domain rules that must always hold. A good domain model maintains many invariants. In other words, it is encapsulated: Khorikov defines encapsulation precisely as the protection of invariants, not as hiding fields.

The opposite of a good model is called anemic. Data lives in some objects and logic in others: DTOs travel around the service, functions change their fields, and there is no structure beyond function signatures. It is easy to slide into such a model when a deadline is close. It looks like this:

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

Two problems jump out. An email is not just any string, yet here you can put anything into it. And `is_employee` depends on the email: if the address is on the corporate domain, the person is an employee. `Person` itself should make that decision, but here it is smeared across services. Sooner or later another `update_person` appears that changes the email and forgets the flag.

It is important not to confuse the anemic model with a transaction script. A transaction script, in Fowler's terms, is an honest pattern: one procedure per business operation. For simple logic, in a supporting subdomain for example, it is an excellent choice. An anemic model is what you get when the logic is complex, the classes are named after domain entities, and they have no behavior. Fowler [calls this an anti-pattern](https://martinfowler.com/bliki/AnemicDomainModel.html): you pay the costs of a domain model without getting its benefits.

### Step one: types instead of primitives {#value-types}

The cheapest refactoring is to replace "dumb" strings and numbers with domain types.

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

`Email`, `Status` and `Discount` are value objects here; more on them below. For now it is enough that you cannot create an `Email` from an invalid string. There is a joke name for code made only of strings: stringly typed, as opposed to strongly typed. If you are not ready to write a value object yet, Python has `typing.NewType`: it adds no checks, but the meaning becomes visible in signatures.

### Step two: behavior moves into the entity {#behaviour}

Types do not protect you from mutable state. Say a customer with more than ten orders gets the Advanced status:

```python
class CustomerService:
    def add_order(self, customer: Customer, product: Product, qty: int) -> None:
        customer.orders.append(Order(product, qty))
        if len(customer.orders) > 10:
            customer.status = Status.ADVANCED
```

The rule lives in the service, and it is easy to bypass: any code can append an order to the list or set the status by hand. If the rule is needed in two places or changes, you will have to hunt for it across the whole project. A good sign is when external code calls one method on an object and the object does everything needed itself. If the caller has to reach inside and check things, there is no encapsulation.

The rule belongs in the entity:

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

From outside, the state can only be read: the status through a property, the orders as an immutable tuple. In Python, privacy is a convention, and an underscore will not stop someone who really wants in. But it clearly marks the boundary, and linters and code review guard it.

The result is a pyramid. At the bottom are value objects: they hold most of the logic, and since they are immutable, they are safe. In the middle are entities: they coordinate value objects and keep invariants. At the top are services that only orchestrate. Refactoring starts at the bottom. The less mutable state there is and the closer the code gets to "the service calls one method on the entity", the better.

## Make the implicit explicit {#implicit-concepts}

Look at this code that books cargo onto a voyage. The example comes from the first chapter of Evans's book:

```python
def book(cargo: Cargo, voyage: Voyage) -> None:
    if voyage.booked + cargo.size > voyage.capacity * 1.1:
        raise BookingError(cargo, voyage)
    voyage.add(cargo)
```

What is `1.1`? Developers did not invent this rule: shipping companies accept 10% more cargo than a vessel can carry, because some customers cancel at the last minute. The rule surely has a name, people discuss it, and some regulation describes it. So it belongs in the model, under the same name:

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

There are more lines now, but the rule can be found, discussed with an expert, tested on its own and replaced. If a rule has no name, it is not in the model. It works the other way round too: when you introduce a new rule, you tidy up the model.

Where to look for such concepts, Evans lists in chapter nine: in the experts' language (a word they keep repeating that the code does not have), in awkward code that is hard to explain, in contradictions between what different experts say, and in the literature of the domain.

## Functional core, imperative shell {#functional-core}

The next principle is known by a name Gary Bernhardt coined: functional core, imperative shell. The audit system example comes from Khorikov. There is a manager that writes visits to files and starts a new file when the current one is full:

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

At the talk someone immediately suggested moving storage work into a separate class. That is the right fix, but it helps to name the problem first: two tasks are mixed here. The first is the rule "if the file is full, start a new one". The second is reading and writing files. The rule cannot be checked without the file system, and tests that touch the file system are slow and brittle.

The algorithmic core should know nothing about input and output: it should only turn some data into other data. Let the core take the contents of the files and return a decision, and let the shell carry it out:

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

Now the rule is checked by an ordinary test on inputs and outputs, with no mocks and no disk:

```python
def test_new_file_is_created_when_the_last_one_is_full() -> None:
    manager = AuditManager(max_entries=2)
    files = [FileContent("audit_0001.txt", ("Peter;2026-04-06T16:30:00", "Jane;2026-04-06T16:40:00"))]

    update = manager.add_record(files, "Alice", datetime(2026, 4, 6, 18, 0))

    assert update == FileUpdate("audit_0002.txt", "Alice;2026-04-06T18:00:00")
```

This gives a simple rule for the whole domain layer: it contains no `await`. If an `await` shows up, I/O has leaked into the domain.

## The trilemma: where to check that an email is free {#trilemma}

This part caused the most arguments at the talk, and for good reason. The task is simple: a user changes their email, but only if no other user has the address. `User` is the main entity here, and its email must never become inconsistent. The question is: who decides that the address is taken?

### Option 1: check in the controller {#check-in-controller}

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

`User.change_email` knows nothing about uniqueness. The decision that the address may be taken is made by external code, not by the entity. Sooner or later an `update_user` appears that changes a dozen fields at once and forgets this check. And if changing the email one day becomes a paid action or starts awarding loyalty points, that logic ends up smeared across controllers. The model is isolated and fast, but not encapsulated.

### Option 2: a repository in the domain {#repository-in-domain}

```python
class User:
    async def change_email(self, email: Email, users: UserRepository) -> None:
        other = await users.get_by_email(email)
        if other is not None and other.id != self.id:
            raise EmailTaken(email)
        self._email = email
```

Now the entity makes the decision itself, and encapsulation is in place. But the audience reacted as one: passing a repository in feels wrong. Someone pointed out that repositories now live in two layers at once, application and domain. Someone else suggested passing a `UserRepository` interface instead of the repository: that is cleaner, but the problem does not go away. An out-of-process dependency has leaked into domain code, and the algorithm can no longer be checked without a database or a mock. And it gets worse: in a real system, locks, retries, transaction rollbacks and writes to a message bus will appear next to the discount calculation. Notice the `async`: the domain has started waiting on the network.

### Option 3: load everything up front {#load-everything}

```python
class User:
    def change_email(self, email: Email, taken: Set[Email]) -> None:
        if email != self._email and email in taken:
            raise EmailTaken(email)
        self._email = email
```

The controller loads every address in use and passes them to the domain. The entity decides by itself and depends on nothing. Elegant, but pointless with a million users. Someone in the audience suggested passing a boolean `taken` flag instead of the set. But who computes it? The controller. That is the first option again.

### Two out of three {#two-of-three}

Vladimir Khorikov calls this the [DDD trilemma](https://enterprisecraftsmanship.com/posts/domain-model-purity-completeness/). His three properties are domain model completeness (all domain logic lives in the domain), purity (the domain has no out-of-process dependencies) and performance. The talk called the first two encapsulation and isolation. You can have only two of the three:

| Option | Encapsulation | Isolation | Performance |
|---|---|---|---|
| Check in the controller | no | yes | yes |
| Repository in the domain | yes | no | yes |
| Load everything up front | yes | yes | no |

The order of sacrifice Khorikov recommends: if you can afford to lose performance, sacrifice it. If not, sacrifice encapsulation. Always keep isolation, because an isolated model is testable. This order is open to argument: a repository in the domain sometimes seems a lesser evil than logic smeared across controllers. But the argument about locks and retries next to business rules wins.

### CanExecute / Execute {#can-execute}

Khorikov offers a compromise that keeps isolation and performance with almost no loss of encapsulation. It is the CanExecute / Execute pattern. Khorikov's example is different: the email cannot be changed once it has been confirmed.

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

The controller decides nothing: it asks the domain, loads data and saves. All decisions, including "is this allowed", stay in `User`. The company is loaded only if the change is allowed, so performance does not suffer.

The check inside `change_email` repeats `can_change_email` on purpose: the operation cannot be called around the check. Khorikov uses a precondition at this point, and the slides in the talk used `assert`. Do not do that in Python: `python -O` strips every `assert`, and the guard silently disappears.

The compromise has a price. Checks that need I/O, such as email uniqueness, still go to the controller. A forgotten `can_*` call surfaces only at runtime. There is more code: a pair of methods for every operation. And for CRUD forms, where the user needs to see all errors at once, the pattern is awkward. It is the best compromise, not a solution to the trilemma.

### What if the requests arrive at the same time {#race}

The audience asked a question that the talk did not really answer: what happens if two people try to take the same address at once? The answer is unpleasant: none of the three options protects against it. Both requests check that the address is free, both get "yes", both save.

The thing is, email uniqueness is a rule about the *set* of users. A `User` entity is responsible only for itself and cannot guarantee anything beyond its own boundary. Rules like this are guaranteed by the database:

```sql
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
```

The domain still states the rule and checks it in the normal case, so it can return a clear error to the user. Under concurrent requests the database constraint holds the rule, and the application layer translates a violation into the same domain error. Address normalization (case, whitespace) lives in the `Email` value object; otherwise `Ann@Example.com` and `ann@example.com` slip past the index. How to catch the constraint violation inside the transaction is shown below, in the Unit of Work section.

## Tactical patterns {#tactical}

The article has been going from the important to the secondary, and what follows is the least important part. Knowing every term for its own sake is pointless. But these are exactly the words that come up in heated debates, so here is a short tour of them.

### Value Object {#value-object}

The value object is the basic building block. It has no identity: two objects are equal when their values are equal. It is immutable: operations return a new object. And it is always valid: it is checked when created.

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

The talk had a good way of putting it: a value object is like a data type. There is the number 5 and another number 5, but they are the same number. A value object works the same way, only smarter: it has invariants, so it is not just a five but a positive five in rubles. Objects with equal values are interchangeable, safe to pass anywhere and easy to test. That is why as much logic as possible should live in value objects.

Forbidding negative amounts is a decision of this model, not a law of nature: in accounting, negative amounts are normal. The same goes for the choice "value object or entity" itself. Evans has an example with an address: an online shop needs an address only as a value telling it where to ship the parcel, while for a postal service that plans delivery routes the address becomes an entity with a life of its own. The answer depends on the context.

### Entity {#entity}

An entity has identity: two entities are equal when their identifiers are equal. It has a lifecycle: its state changes while its id stays the same. An entity protects its own invariants, changes only through its methods, and delegates complex logic to value objects.

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

`Order` takes care of the lifecycle, `Money` of the rules for money. Two orders that match in everything but the id are not interchangeable. And a Python-specific detail: if you define `__eq__` without `__hash__`, Python sets `__hash__ = None`, and the entity can no longer go into a set or serve as a dictionary key.

### Aggregate {#aggregate}

An aggregate groups entities and value objects under one root. Such a group is stored and changed only as a whole. The objects inside can be reached only through the root, and changed only through it. If a car has wheels, you cannot get to a wheel other than through the car's interface.

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

The invariant "the order total does not exceed the limit" involves all lines at once, which is why the lines live inside the aggregate. You can read the lines but not change them directly: encapsulation protects invariants, not data. The order refers to other aggregates, such as the customer or a product, only by id.

Importantly, the aggregate exists in the model, not in the database. The database has no "root": there is a parent table `orders` and a child table `order_lines`, and `Money` is not a table at all but a pair of columns in a row.

Aggregates come with a rule that Vaughn Vernon puts this way: the aggregate boundary is the transaction boundary, and one transaction changes one aggregate. The examples below break it: changing an email changes both the user and the company. In a single PostgreSQL database that is a pragmatic choice, but it has a cost: the aggregates become coupled and compete for locks. If two aggregates constantly need to change together, the boundary may be drawn in the wrong place. If they do not, the second change can be made eventually consistent through a domain event.

### Repositories and factories {#repository}

In DDD, a repository saves and restores aggregates: domain objects, that is, not rows and not DTOs. One repository per aggregate: there is an `OrderRepository`, but no `OrderLineRepository`. The repository assembles the aggregate from rows and takes it apart again:

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

`_db` here is just a thin wrapper over the connection, so the SQL does not get in the way. In real code an ORM does this work.

In Evans's book a factory creates an object atomically, valid from the start. But restoring from the database is not the same as creating. On creation, a broken invariant means bad input, and the factory simply refuses to create the object. On restoration, the object already exists, and a broken invariant means corrupted data: you need to react differently, but pretending everything is fine is not an option either.

And one last rule from the same chapter of Evans: the client controls the transaction, not the repository. A repository does not commit. Why this matters and what breaks otherwise, is covered in detail in the [article on SQLAlchemy sessions and transactions](2026-10-08-sqlalchemy-sessions-and-transactions.md).

### Does a repository need an interface {#abstract-repository}

Robert Martin's clean architecture says yes: the domain declares an interface, the infrastructure implements it, dependencies point inward, the database becomes a detail, and business rules can be tested without it.

Khorikov answers differently. There is one repository implementation, and the interface exists only for mocks. But your own database is a managed dependency: you do not mock it, you verify it with integration tests. No mocks means no need for the interface. Abstractions are discovered, not invented: when a second implementation appears, that is when you extract an interface. The authors of "Architecture Patterns with Python" take a third position: an abstract repository plus an in-memory `FakeRepository` on which the service layer is tested quickly.

A reasonable synthesis looks like this. If the domain is pure, as in the section on the functional core, only the application layer calls repositories, and clean architecture's main argument, "the domain must not depend on the database", resolves itself: the domain does not depend on repositories anyway. An interface is justified when a second implementation has actually appeared. The talk brought up exactly such a case: a caching repository decorator on top of the regular one, with the same protocol. Besides, a `Protocol` in Python is cheap: implementations do not have to inherit from it, so an extra abstraction costs little.

### Reads that bypass aggregates {#reads}

Another question from the audience: if a repository returns only aggregates, what about reads that need joins across five tables and pagination? Building full aggregates for a list of orders is expensive and pointless.

So do not. Aggregates exist to *change* state while keeping invariants. A read changes nothing, so a query can bypass the model, go straight to SQL and return a flat structure shaped for the screen. This is a lightweight form of CQRS: commands go through aggregates, queries go separately.

While on the subject, a popular misconception. At the talk someone said that Fowler considers DTOs an anti-pattern. He does not: the Data Transfer Object is described in Fowler's own book as a pattern for passing data between processes. What he criticizes is the [LocalDTO](https://martinfowler.com/bliki/LocalDTO.html), a DTO inside a single process, where DTOs multiply code and push you toward an anemic model. Declaring all DTOs evil is Yegor Bugayenko's position. The compromise is simple: DTOs at the boundaries (the API, a queue, the result of a read query), behavior inside the model.

### Unit of Work {#unit-of-work}

Suppose each repository has its own connection. Then an email change can end like this: the company is saved, the user is not. You need a shared transaction, and this is where Unit of Work comes in. Fowler defines it this way: it maintains a list of objects affected by a business transaction and coordinates the writing out of changes and the resolution of concurrency problems. In other words, it accumulates changes and writes them at the end in one batch: the transaction is shorter, with fewer locks and fewer queries.

Strictly speaking, Unit of Work is not a DDD pattern but a data storage pattern from Fowler's catalog; DDD merely relies on it. In Python hardly anyone writes it by hand: [the `Session` in SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) already implements Unit of Work together with an identity map: it tracks changed objects itself and writes them on commit.

What remains is to decide who owns the transaction and how application code gets its repositories. DDD code usually says `uow.orders.add(order)`: the repositories live inside the Unit of Work. In [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/) this is `AsyncSQLAlchemyUnitOfWork`: each `transaction()` opens its own session, commits on a normal exit and rolls back on an exception, and the transaction object hands out the repositories of one bounded context:

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

For the race from the trilemma section, it matters where a violation of `uq_users_email` surfaces. If the repository runs its UPDATE immediately, the error comes straight out of `save()`. If changes wait in the session, they are sent by the `flush()` that `transaction()` runs before committing by default. Either way an `IntegrityError` leaves `transaction()`, and it can be translated into a domain error. Below, this is put together with domain events.

### Domain Events {#domain-events}

The last tactical pattern removes one more out-of-process dependency from the domain. Suppose that after an email change the service has to send a message to a bus. You could send it right from `User.change_email`, but then the domain gets a bus, and with it I/O, retries and everything the trilemma section was running away from.

Instead, the entity records what happened and does nothing more:

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

The decision is in the domain, the sending happens outside: the user does not even know there is a bus somewhere. Domain events, by the way, are not in Evans's original 2003 book. They were added later: by Vernon in the red book and by Evans himself in the DDD Reference.

Sending events after the commit is unreliable, and the talk said so openly. If the process dies between the commit and the send, the event is lost. If you send before the commit and the transaction rolls back, the world learns about an email change that never happened. The reliable option is called the transactional outbox: the event is written as a row in the same transaction as the aggregate's changes, and a separate process publishes such rows to the broker. The scheme is covered in detail in the [article on Outbox and Inbox](2026-10-03-reliable-events-outbox-inbox-kafka.md). In [omni-box](https://bedrock-python.github.io/omni-box/) the outbox event fields are even named in DDD's language: `aggregate_type` and `aggregate_id`.

What remains is to add the outbox to the transaction object and put the whole operation together:

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

`is_unique_violation` checks for SQLSTATE `23505` and the constraint name; its asyncpg implementation is in the [lab](../lab/2026-11-02-domain-driven-design/README.md). The user, the company and the event are saved together or not at all. The constraint is the check here: whether the address was taken long ago or a concurrent request got there a millisecond earlier, the user gets the same error. The lab reproduces the race: two transactions both read the address as free, and only one of them manages to commit. The function itself contains no business decisions: it loads, asks the domain, and saves.

### Domain layer and application layer {#domain-vs-application}

The main part of the talk ended with a question: how does the domain layer differ from the application layer? The domain layer answers "how": how to transfer money, how to change an email. The application layer answers "what needs to be done": it is a simple, almost dumb script that loads complex objects, calls their methods and saves them. The `change_email` function above belongs to the application layer.

```python
def transfer(source: Account, target: Account, amount: Money) -> None:
    if source.currency != target.currency:
        raise CurrencyMismatch(source.currency, target.currency)
    source.withdraw(amount)
    target.deposit(amount)
```

A transfer between accounts involves two objects and belongs to neither of them. Evans calls such an operation a domain service; in clean architecture an application scenario is called a use case, elsewhere a handler or an application service. The names do not matter; the layer does: decisions in the domain, coordination in the application layer.

### Specification {#specification}

At the talk this pattern was skipped as boring, but the audience asked for at least a brief version. Sometimes a business rule does not fit into a single entity: it combines conditions, uses other concepts, and you also need to search the database by it. Then the rule becomes a value object of its own. Evans's classic example is an overdue invoice that takes the customer's grace period into account.

```python
@dataclass(frozen=True)
class DelinquentInvoice:
    today: date

    def is_satisfied_by(self, invoice: Invoice) -> bool:
        return self.today > invoice.due_date + invoice.customer.payment_grace_period
```

The same specification checks an object in memory and, translated into a query condition, selects matching rows from the database. Specifications can be combined with "and", "or" and "not". The point is that the rule has one home, so the check and the search never drift apart. In Python this is often overkill: as long as the rule depends only on the entity's own fields, an `invoice.is_overdue(today)` method is enough.

## DDD and tests {#testing}

Testing was promised at the start, and it is probably what shows best why all this fuss about isolation is worth it. Khorikov sorts code along two axes: how complex or important it is to the domain, and how many collaborators it has.

| | Few collaborators | Many collaborators |
|---|---|---|
| **Complex or important** | domain model and algorithms: unit tests | overcomplicated code: refactor |
| **Simple** | trivial code (DTOs, getters): do not test | controllers: integration tests |

The domain model is covered by unit tests entirely and without a single mock: there is nothing in it to mock. Controllers are checked by integration tests, and that is the only place mocks appear. Overcomplicated code, which decides and coordinates at the same time, has to be split into the other two quadrants. The `AuditManager` test above belongs to the top-left quadrant.

At the talk someone asked a fair question: why test the domain separately if the controller scenarios go through it anyway? An integration test does cover more and shows more. But it is more expensive to write: it needs a lot of setup. It is hard to reach every branch with it: getting into each `if` takes contrived test data. It is slow, because it works with the database. And it is harder to maintain. Part of this argument weakens when an AI agent writes the tests: the setup costs it almost nothing. But that does not make integration tests any faster, and reaching every `if` with them is still hard. If integration tests ran instantly and cost nothing to write, you could write only those. Many teams largely live like that, but the classic position is that fast unit tests on the domain give better feedback.

### What to mock {#what-to-mock}

| Dependency | Example | What to do |
|---|---|---|
| In-process | domain, value objects, entities | real objects, no mocks |
| Managed | your own database, visible only to your service | a real database in integration tests |
| Unmanaged | message bus, SMTP, third-party API, visible to other systems | a mock: this is observable behavior |

A database mock checks *how* the code writes, not *what* ends up stored, and it breaks with every refactoring. Unmanaged dependencies are mocked at the very edge of the system, on the last type before the network:

```python
class Bus(Protocol):  # the only interface: the last type before the network
    def send(self, message: str) -> None: ...


class MessageBus:
    def __init__(self, bus: Bus) -> None:
        self._bus = bus

    def send_email_changed(self, user_id: UUID, email: Email) -> None:
        self._bus.send(f"Type: USER EMAIL CHANGED; Id: {user_id}; NewEmail: {email}")
```

The test mocks `Bus`, not `MessageBus`, and checks exactly the string that goes over the network. With an outbox the picture is even simpler: the message first becomes a row in the service's own database, and the integration test checks that row. A broker mock is needed only in the publisher's tests.

### Public API {#public-api}

Test observable behavior, not implementation details. Private methods are tested through public ones. If you want to test a private method or patch something inside a class, that is a design signal: most likely a separate object is hiding in there, one that lacks a name. And the higher the level of an object, the more its API should resemble the language of the domain: an aggregate's public API is its contract in the ubiquitous language.

## When you do not need DDD {#when-not-to-use}

The last question from the audience was the most honest one: why all this, when you can put the code into three folders, `core`, `infra` and `use_cases`, and live without extra concepts?

Often you do not need it. DDD pays off when the domain is complex and you do not fully understand it yourself. When you are not your own customer. When many people are involved and each knows their own piece. When mistakes are not an option: if you grant people loans, you need to know exactly which rule applies and where it is written down. The complexity here is in the logic, not the load: high RPS has nothing to do with DDD. If a service moves data from Kafka to PostgreSQL, it needs no model, and a transaction script will be more honest.

Why patterns at all? Fowler has the [Design Stamina Hypothesis](https://martinfowler.com/bliki/DesignStaminaHypothesis.html): without design you are faster at first, but over time every feature costs more, and at some point you are overtaken by whoever invested in structure. Greedy in-place fixes give a fast start, and then every change breaks its neighbors, tests fail on refactoring, and before each release nobody is sure the system works. A good model gives you the opposite: new behavior is added next to existing code, not across it. Plugging another provider into such code comes down to a new implementation of an interface, and the rest of the code does not change.

And one last thought. With AI agents in development, the strategic ideas of DDD seem to be gaining weight, while the tactical ones are losing it. An agent, like a new person on the team, needs a vocabulary and boundaries: which concepts the system has, what they mean in this context, and which rules must not be broken. An agent will write pattern-shaped code on its own, but it will not invent the model for you. Even the testing debate shifts: an agent writes an integration test almost for free, so the main case left for unit tests on the domain is fast feedback, not the cost of writing. How to prepare that kind of context for agents is covered in the [article on documentation for AI coding agents](2026-10-26-documentation-for-ai-coding-agents.md).

## Further reading {#sources}

- Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003). The blue book, where it all started. An updated summary of the patterns: [*Domain-Driven Design Reference*](https://www.domainlanguage.com/ddd/reference/) (2015).
- Vaughn Vernon, *Implementing Domain-Driven Design* (2013). The red book, more practical than the blue one.
- Vladimir Khorikov, *Unit Testing Principles, Practices, and Patterns* (2020). Half of the book is really about how to structure a domain model. The quadrants, managed dependencies and CanExecute / Execute come from here.
- Vlad Khononov, *Learning Domain-Driven Design* (2021). The best source on subdomains and on how much DDD to spend on each.
- Harry Percival and Bob Gregory, [*Architecture Patterns with Python*](https://www.cosmicpython.com/) (2020). Repositories, Unit of Work, aggregates and events in Python with SQLAlchemy.
- Martin Fowler, *Patterns of Enterprise Application Architecture* (2002): Unit of Work, Transaction Script, Data Transfer Object.
