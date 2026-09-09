---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - servicewright
  - grpc
  - fastapi
  - errors
  - api-design
---

# Ошибки без привязки к транспорту: одна ошибка предметной области, ответы HTTP и gRPC {#transport-independent-errors-one-domain-error-http-and-grpc-responses}

<div class="bdr-post__hero" data-bdr-post="2026-09-07-transport-independent-errors" role="img" aria-label="Одна ошибка предметной области и две корректные формы ответа" markdown="0"></div>

Сервис с внешним HTTP и внутренним gRPC формирует два ответа на каждый сбой, и они расходятся. HTTP-обработчик учится возвращать problem document, gRPC-сервис — вызывать `context.abort`. Где-то `NotFound` становится 404 в одном месте и `UNKNOWN` с внутренними подробностями в другом. Решение начинается с разделения: предметная область называет случившееся, каждый транспорт знает, как сообщить об этом.

<!-- more -->

Числа получены в [эксперименте статьи](../lab/2026-09-07-transport-independent-errors/README.md): один сценарий использования доступен через FastAPI и gRPC; каждый случай вызывается обоими способами. Версии: servicewright 0.10.1, grpcio 1.83.1, Python 3.13.

## Предметная область выбрасывает ошибки, а не форматирует их {#the-domain-raises-and-does-not-format}

```python
class OrderNotFoundError(ServiceError):
    kind = ErrorKind.NOT_FOUND


class LedgerCorruptedError(ServiceError):
    kind = ErrorKind.INTERNAL
    public = False


async def pay_order(order_id: str) -> Receipt:
    ...
    raise OrderNotFoundError("no order with id 42", params={"order_id": "42"})
```

Основную работу делают два свойства. **`kind`** описывает категорию сбоя языком предметной области: не найдено, конфликт, запрещено, недоступно. Транспорт переводит её в свой набор кодов. **`public`** определяет, допустимо ли раскрывать подробности клиенту.

Остальное выводится автоматически. Код ошибки — имя класса в snake case: `OrderNotFoundError` превращается в `order_not_found` без повторного ручного написания строки.

## Семь вызовов через два транспорта {#the-same-seven-calls-two-transports}

```text
    case         HTTP                                       gRPC
    missing      404 code=order_not_found                   NOT_FOUND  [x-error-code=order_not_found]
                 detail="no order with id 42"               "no order with id 42"
    paid         409 code=order_already_paid                ALREADY_EXISTS  [x-error-code=order_already_paid]
    forbidden    403 code=not_your_order                    PERMISSION_DENIED  [x-error-code=not_your_order]
    provider     503 code=payment_provider_down             UNAVAILABLE  [x-error-code=payment_provider_down]
    ledger       500 code=internal_error, no detail         INTERNAL: internal_error  [x-error-code=internal_error]
    unexpected   500 code=internal_error, no detail         INTERNAL: internal_error  [x-error-code=internal_error]
    ok           200                                        OK
```

Ни один обработчик не содержит `try`. HTTP возвращает словарь, gRPC — bytes. Отображение задано один раз в транспортном слое.

В таблице важны три вещи.

**Статус переводится в понятия протокола.** `ErrorKind.CONFLICT` даёт HTTP 409 и gRPC `ALREADY_EXISTS`. Это единое решение на категорию. У gRPC меньше и более общие статусы, поэтому выбор `ALREADY_EXISTS` или `ABORTED` для конфликта состояния можно обсуждать. Главное — обсуждение одной таблицы, а не сорока обработчиков.

**Код ошибки сохраняется.** Trailing metadata `x-error-code` передаёт gRPC-клиенту `order_already_paid`, уточняя общий статус. Если нужно отличить дубликат от неправильного состояния, клиент читает этот код. В HTTP та же строка — поле problem document. Один словарь, две оболочки.

**Последние две строки одинаковы намеренно.** `ledger` — `ServiceError` с `public=False`, `unexpected` — обычный необъявленный `RuntimeError`. Оба транспорта возвращают общую внутреннюю ошибку без подробностей; настоящее сообщение и traceback остаются в журнале. Клиенту не нужно знать, повреждён ledger или кто-то поделил на ноль.

Последняя строка часто ломается: объявленные ошибки обработаны внимательно, остальные уходят в стандартное поведение фреймворка. У gRPC оно раскрывает представление исключения в details. В эксперименте сообщение безобидно; исследование началось со строки подключения с паролем.

## Что разрешено знать слоям {#what-each-layer-is-allowed-to-know}

Правило против постепенного расползания: **предметная область не импортирует транспорт, а общий транспортный слой не знает конкретных классов ошибок сценария**.

Предметная область называет сбой. Сценарий выбрасывает `OrderNotFoundError` и делал бы это даже в CLI. Он не выбирает статусы, новый транспорт его не меняет.

Транспорт переводит категории. HTTP знает соответствия kind и статуса и формат problem document. gRPC-слой знает статусы gRPC и trailing metadata. Ни у одного нет ветки для `OrderNotFoundError`, поэтому новая ошибка в существующей категории не требует правки транспортов.

Остаются два решения. *Публичны ли подробности?* Это оценка содержания, поэтому она живёт на классе ошибки. *Что делать, если никто не решил?* Это общая политика: скрывать, с обработкой всех остальных исключений на внешней границе транспорта. Именно неучтённое иначе и утечёт.

## Один согласованный тест {#testing-it-once}

Проверять стоит не только HTTP 404, а согласованность транспортов:

```python
@pytest.mark.parametrize("error, kind", CASES)
def test_both_transports_say_the_same_thing(error, kind):
    ...
```

Один параметризованный тест проходит ошибки предметной области и проверяет HTTP-статус, gRPC-статус и общий код. Он падает, если новая категория попала лишь в одну таблицу. Нужен и случай, который вообще не является `ServiceError`: именно он здесь дал регрессию.

## Чего это не решает {#what-this-does-not-solve}

Пользовательские *тексты* ошибок сюда не относятся. `detail` адресован разработчику; текст интерфейса выбирается по коду на языке пользователя. Переведённые пользовательские фразы в `detail` заставили бы backend владеть текстами интерфейса.

Повторяемость тоже не определяется автоматически. `UNAVAILABLE` может разрешать повтор, `INVALID_ARGUMENT` — нет. Выбирая kind, явно оцените этот смысл. Неудачная категория может создать лавину повторов на стороне клиента — [вопрос надёжности](2026-09-07-reliability-is-not-retry-3.md), только со стороны сервера.

## Инструменты {#the-pieces}

Модель предоставляет [servicewright](https://bedrock-python.github.io/servicewright/): `ServiceError` с `kind`, `code`, `public`, таблица на транспорт, HTTP problem documents RFC 9457, gRPC-перехватчик и обработка неизвестных исключений с маскированием. Общая защита gRPC появилась в 0.10.1, потому что этот эксперимент обнаружил её отсутствие.

Семь вызовов, два транспорта, одна таблица результатов. Главная строка — необъявленное исключение.
