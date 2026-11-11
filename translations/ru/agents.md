---
title: Для ИИ-агентов
description: Индекс репозиториев Bedrock Python для ИИ-ассистентов. Для чего каждая библиотека и инструмент, когда их брать и где их собственная страница для агентов.
copy_page: true
---

# Bedrock Python для ИИ-агентов

> Индекс всех репозиториев Bedrock Python для ИИ-ассистента, который собирает
> продакшн-сервис на async Python: для чего каждая библиотека и инструмент, когда их брать
> и где их собственная страница для агентов. Дайте агенту сначала эту страницу. По ней он
> выберет библиотеки, а API прочитает на их страницах.

## Как читать эту страницу

У каждой библиотеки есть одностраничный справочник для ассистентов:
`https://bedrock-python.github.io/<repo>/agents/`, его Markdown лежит по адресу
`https://bedrock-python.github.io/<repo>/agents.md`. Markdown этой страницы:
`https://bedrock-python.github.io/ru/agents.md`, английской версии:
`https://bedrock-python.github.io/agents.md`.

Здесь нет API и нет кода. Страница говорит, какой репозиторий решает какую задачу и как
библиотеки стыкуются в одном сервисе. Прежде чем писать код под библиотеку, загрузите её
страницу для агентов: имена, сигнатуры и правила находятся там.

## Что брать под какую задачу

Берите только то, что сервису нужно. Сервису на этом стеке нужен Python 3.12 или новее.

| Сервису нужно | Берите |
|---|---|
| Один жизненный цикл процесса для HTTP, gRPC, cron, демонов и разовых задач | [servicewright](#servicewright) |
| PostgreSQL через асинхронную SQLAlchemy | [sqlalchemy-foundation-kit](#sqlalchemy-foundation-kit) |
| Миграции Alembic, проверенные до продакшна | [alembic-gauntlet](#alembic-gauntlet) |
| События уходят ровно при коммите транзакции, сообщения обрабатываются один раз | [omni-box](#omni-box) |
| Повторный запрос не должен выполниться дважды | [idempotency-kit](#idempotency-kit) |
| Таблицы, секционированные по времени | [pg-partsmith](#pg-partsmith) |
| Redis | [redis-client-kit](#redis-client-kit) |
| Kafka | [aiokafka-foundation-kit](#aiokafka-foundation-kit) |
| Исходящие HTTP-вызовы | [clientwright](#clientwright) |
| gRPC-сервер | [servicewright](#servicewright) вместе с [grpc-server-kit](#grpc-server-kit) |
| gRPC-клиент | [grpc-client-kit](#grpc-client-kit) |
| Один бюджет времени на запрос для всех вызовов вниз по цепочке | [deadline-budget](#deadline-budget) |
| Одинаковые инструкции для агентов и CI-файлы во всех репозиториях | [touchmark](#touchmark) вместе с [engineering-assets-template](#engineering-assets-template) |
| Своя новая библиотека | [python-library-template](#python-library-template) |
| Ревью кода моделью | [mr-review](#mr-review) |

## Рантайм

### servicewright

Основа любого сервиса. Проводит один процесс через один жизненный цикл: запуск, прогрев,
готовность, работа, плавная остановка, очистка. Одно описание сервиса запускается с любым
списком точек входа: приложение FastAPI или Litestar, gRPC-сервер, cron-планировщик, цикл
демона, разовая задача. Так API и его воркер остаются одной кодовой базой и одним образом.
Он владеет сигналами, пробами здоровья, плавной остановкой и настройкой логов, метрик,
трассировки и трекинга ошибок. DI-контейнера и бизнес-логики в нём нет; dishka
подключается через адаптер.

Берите для каждого сервиса и начинайте с него: остальные библиотеки подключаются к его
контейнеру и жизненному циклу.

Страницы: [для агентов](https://bedrock-python.github.io/servicewright/agents/) ·
[структура проекта](https://bedrock-python.github.io/servicewright/blueprints/project-layout/) ·
[blueprint HTTP API](https://bedrock-python.github.io/servicewright/blueprints/http-api/) ·
[blueprint воркера](https://bedrock-python.github.io/servicewright/blueprints/worker/)

## Данные

### sqlalchemy-foundation-kit

Слой PostgreSQL, который сервис иначе писал бы сам: асинхронный движок и менеджер сессий с
пулом и настройками, безопасными для PgBouncer, Unit of Work, сейвпоинты, advisory-локи,
метрики пула и декларативный `Base` с соглашением об именах ограничений.

Берите, когда сервис работает с PostgreSQL через SQLAlchemy и asyncpg. Репозиториев,
миграций и синхронного API в нём нет.

Страница: [для агентов](https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents/)

### alembic-gauntlet

Набор для pytest, который прогоняет настоящую историю Alembic на настоящем PostgreSQL во
временной схеме. Один унаследованный тестовый класс даёт семь тестов: каждая миграция
вверх и вниз по шагам, сравнение результата с ORM-моделями, имена ограничений, значения
enum, единственная голова.

Берите как dev-зависимость, когда у сервиса есть миграции Alembic. В продакшне миграции он
не запускает.

Страница: [для агентов](https://bedrock-python.github.io/alembic-gauntlet/agents/)

### omni-box

Транзакционные outbox и inbox. Outbox: строка события пишется в той же транзакции, что и
бизнес-состояние, а ретранслятор позже отправляет её в брокер. Inbox: входящие сообщения
дедуплицируются, обработчик выполняется в той же транзакции, что и строка inbox.

Берите, когда событие нельзя потерять или отправить без изменения в базе, или когда
консьюмер не должен обработать сообщение дважды. Транзакцией, миграциями и планировщиком
он не владеет: таблицы идут в ваши миграции, цикл ретранслятора в ваш воркер.

Страница: [для агентов](https://bedrock-python.github.io/omni-box/agents/)

### idempotency-kit

Кеширует результат операции под ключом, который прислал клиент, и отдаёт его при повторе.
Держит ключ, пока идёт первый вызов, и может отказать, если ключ повторно использован с
другим телом запроса. Состояние хранится в Redis.

Берите для записей по HTTP или gRPC, которые клиенты повторяют: платежи, создание заказа.
Это не распределённый лок и не транзакция.

Страница: [для агентов](https://bedrock-python.github.io/idempotency-kit/agents/)

### pg-partsmith

Держит секционированную по времени таблицу PostgreSQL в заданном виде: заранее создаёт
секции, отцепляет устаревшие и удаляет их после паузы, с планом, который можно посмотреть
заранее. Библиотека и CLI, есть и образ контейнера.

Берите, когда таблица секционирована по времени: события, логи, outbox со сроком хранения.
Родительская таблица и её индексы остаются в ваших миграциях, расписание тоже ваше:
вызывайте его из задачи по расписанию или Kubernetes CronJob.

Страница: [для агентов](https://bedrock-python.github.io/pg-partsmith/agents/)

### redis-client-kit

Собирает настроенный клиент redis-py, для одного узла или кластера, из одного объекта
настроек, с метриками, проверкой здоровья и аккуратным закрытием. Возвращает обычный
клиент redis-py.

Берите всегда, когда сервис работает с Redis. Кеша, локов и префиксов ключей он не
добавляет.

Страница: [для агентов](https://bedrock-python.github.io/redis-client-kit/agents/)

## Сообщения и вызовы других сервисов

### aiokafka-foundation-kit

Собирает продюсеры и консьюмеры aiokafka из настроек и управляет их запуском и
остановкой. Ещё создаёт топики и проверяет здоровье кластера.

Берите, когда сервис пишет в Kafka или читает из неё. Цикла потребления, ретраев и
dead-letter топика в нём нет: цикл это точка входа servicewright, которую пишете вы, а
однократная обработка это inbox из omni-box.

Страница: [для агентов](https://bedrock-python.github.io/aiokafka-foundation-kit/agents/)

### clientwright

Собирает нативный HTTP-клиент, которым вы уже пользуетесь (httpx, aiohttp, requests,
urllib3), с одним движком под ним: общий дедлайн, ретраи с бюджетом, circuit breaker,
подстановка заголовков, метрики и трассировка.

Берите для каждого исходящего HTTP-вызова. Второй слой ретраев сверху не добавляйте.

Страница: [для агентов](https://bedrock-python.github.io/clientwright/agents/)

### grpc-server-kit

Всё вокруг асинхронного gRPC-сервера, кроме ваших сервисеров: проверенные опции, TLS,
плавная остановка, интерсепторы с поддержкой стриминга, стандартный health-сервис.

В сервисе не начинайте с него: extra `grpc` у servicewright построен на нём и ставит
сервер под тот же жизненный цикл, что и всё остальное. Его страницу читайте ради
интерсепторов, TLS и настроек сервера.

Страница: [для агентов](https://bedrock-python.github.io/grpc-server-kit/agents/)

### grpc-client-kit

Вызывающая сторона gRPC: пул каналов, выбор цели с учётом здоровья и одна цепочка
интерсепторов с таймаутами, ретраями, circuit breaker, метриками и трассировкой для всех
четырёх видов RPC.

Берите для каждого исходящего gRPC-вызова. Только async.

Страница: [для агентов](https://bedrock-python.github.io/grpc-client-kit/agents/)

### deadline-budget

Арифметика над одним обратным отсчётом на запрос: сколько секунд можно дать следующему
вызову с учётом остатка, лимитов на вызов и резерва на ответ.

Берите, когда один запрос делает несколько вызовов и должен уложиться в общее время. Сам
он ничего не обрывает: бюджет применяют clientwright и grpc-client-kit через свой extra
`deadline`.

Страница: [для агентов](https://bedrock-python.github.io/deadline-budget/agents/)

## Инструменты и стандарты репозиториев

### touchmark

Держит общие файлы одинаковыми во многих репозиториях через pull request и никогда не
перезаписывает файл, который команда изменила. Это движок хаба engineering-assets.
Работает с GitHub, GitLab, Gitea, Forgejo, Bitbucket и Azure DevOps.

Берите, когда в нескольких репозиториях должны лежать одинаковые `AGENTS.md`, гайдлайны,
промпты для ревью или CI-файлы.

Страница: [для агентов](https://bedrock-python.github.io/touchmark/agents/)

### engineering-assets-template

Шаблон вашего собственного хаба: репозиторий с паками общих файлов и списком целевых
репозиториев. Для сервиса в нём есть паки `agents` (`AGENTS.md`, профиль проекта, промпты
для ревью), `python-service` (гайдлайны по Python, тестам и базе данных, скиллы для
запуска и тестов сервиса) и `claude` (инструкции Claude Code, настройки, сабагент-ревьюер).

Берите один раз на организацию. Репозиторий сервиса потом подписывается файлом
`.engineering-assets.yml` и заполняет `.agents/project.md`, который остаётся его
собственным.

Репозиторий: [engineering-assets-template](https://github.com/bedrock-python/engineering-assets-template)

### engineering-assets

Собственный хаб организации Bedrock Python, созданный из шаблона. Доставляет во все
здешние библиотеки ассеты сайта документации, общие файлы сообщества и инструкции для
агентов. Смотрите на него как на рабочий пример хаба; в репозитории вне организации он
ничего не доставляет.

Репозиторий: [engineering-assets](https://github.com/bedrock-python/engineering-assets)

### python-library-template

Шаблон Copier для новой Python-библиотеки со структурой, принятой в организации: uv, ruff,
mypy, тесты, сайт документации со страницей для агентов, автоматизация релизов.

Берите, когда выносите общий код в собственную библиотеку. Для сервисов не подходит.

Репозиторий: [python-library-template](https://github.com/bedrock-python/python-library-template)

### mr-review

Инструмент, который разворачивается у себя и делает ревью merge request языковой моделью.
Подключается к GitLab, GitHub, Gitea, Forgejo или Bitbucket, работает с Claude, OpenAI и
любой OpenAI-совместимой моделью.

Страница: [для агентов](https://bedrock-python.github.io/mr-review/agents/)

### mattermind

Отвечает на вопросы о рабочем пространстве Mattermost на естественном языке: модель
вызывает инструменты. В стек сервиса не входит.

Страница: [для агентов](https://bedrock-python.github.io/mattermind/agents/)

## Порядок сборки

1. **Каркас.** servicewright с его структурой проекта: настройки, контейнер dishka, одно
   описание сервиса, по одному main на процесс (`api_main`, `worker_main`).
2. **База.** sqlalchemy-foundation-kit для сессий и Unit of Work; модели на его `Base`.
3. **Миграции.** Alembic, а alembic-gauntlet в тестах с первой же миграции.
4. **Записи, которые клиенты повторяют.** redis-client-kit для клиента, поверх него
   idempotency-kit.
5. **События.** outbox из omni-box в пути записи, ретранслятор в воркере,
   aiokafka-foundation-kit для продюсера; inbox из omni-box для консьюмеров.
6. **Вызовы других сервисов.** clientwright для HTTP, grpc-client-kit для gRPC,
   deadline-budget, когда один запрос делает несколько таких вызовов.
7. **Эксплуатация.** Проверки здоровья и метрики для каждого процесса через
   servicewright; pg-partsmith для секционированных таблиц.
8. **Репозиторий.** Инструкции для агентов и гайдлайны из вашего хаба engineering-assets.

## Где библиотеки стыкуются

Факты, которых нет ни на одной странице отдельной библиотеки. Они проверены сборкой одного
сервиса из опубликованных версий библиотек и его запуском на PostgreSQL, Redis и Kafka.

- servicewright владеет процессом и контейнером dishka. Каждая другая библиотека даёт
  провайдер dishka или клиент, который создаётся один раз на процесс. Ничего не создаётся
  на каждый запрос или при импорте.
- Каждая библиотека запрашивает свои настройки по собственному типу-протоколу. Один
  провайдер в сервисе раздаёт каждой библиотеке её секцию настроек.
- Провайдер базы из sqlalchemy-foundation-kit запрашивает ещё и
  `PostgresMetricsProtocol | None`. Предоставьте его, даже когда метрики выключены, иначе
  контейнер не соберётся.
- Провайдер Redis из idempotency-kit берёт ровно тот клиент, который даёт провайдер
  redis-client-kit. Связующий код не нужен.
- omni-box не использует Unit of Work. Передавайте его репозиторию сессию текущей
  транзакции, чтобы событие закоммитилось вместе с бизнес-изменением.
- Таблицы omni-box идут в ваши метаданные и миграции Alembic. Их индексы называются
  `idx_...`, а соглашение sqlalchemy-foundation-kit заканчивает имена на `_idx`:
  разрешите префикс `idx_` в тесте имён alembic-gauntlet.
- В `env.py` Alembic передавайте `version_table_schema` только для схемы, отличной от
  `public`. Явный `public` заставляет autogenerate добавить удаление `alembic_version`.
- Проверки здоровья Postgres и Redis из servicewright принимают session maker и клиент,
  которые собирают эти два кита.
- clientwright и grpc-client-kit держат бюджет запроса каждый в своём контексте. Сервис,
  который использует оба, устанавливает бюджет в оба.
- Планировщик в servicewright работает внутри процесса. Держите его в одной реплике.
- У APScheduler 4 есть только пре-релизы, которые pip и uv по умолчанию пропускают. Extra
  `apscheduler3` ставится без флагов.

## Страницы для агентов

| Репозиторий | Страница |
|---|---|
| servicewright | <https://bedrock-python.github.io/servicewright/agents.md> |
| sqlalchemy-foundation-kit | <https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents.md> |
| alembic-gauntlet | <https://bedrock-python.github.io/alembic-gauntlet/agents.md> |
| omni-box | <https://bedrock-python.github.io/omni-box/agents.md> |
| idempotency-kit | <https://bedrock-python.github.io/idempotency-kit/agents.md> |
| pg-partsmith | <https://bedrock-python.github.io/pg-partsmith/agents.md> |
| redis-client-kit | <https://bedrock-python.github.io/redis-client-kit/agents.md> |
| aiokafka-foundation-kit | <https://bedrock-python.github.io/aiokafka-foundation-kit/agents.md> |
| clientwright | <https://bedrock-python.github.io/clientwright/agents.md> |
| grpc-server-kit | <https://bedrock-python.github.io/grpc-server-kit/agents.md> |
| grpc-client-kit | <https://bedrock-python.github.io/grpc-client-kit/agents.md> |
| deadline-budget | <https://bedrock-python.github.io/deadline-budget/agents.md> |
| touchmark | <https://bedrock-python.github.io/touchmark/agents.md> |
| mr-review | <https://bedrock-python.github.io/mr-review/agents.md> |
| mattermind | <https://bedrock-python.github.io/mattermind/agents.md> |
