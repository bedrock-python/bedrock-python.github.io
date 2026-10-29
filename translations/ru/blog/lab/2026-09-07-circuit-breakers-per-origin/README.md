# Практикум: Отдельный circuit breaker для каждого origin {#lab-circuit-breakers-should-be-per-origin}

Один HTTPX-клиент обращается к двум локальным HTTP-серверам: складу и оплате. Оплата всегда отвечает 503. Три вызова дают девять попыток; четвёртый отклоняется, не достигнув сервера. Склад продолжает отвечать 200.

Отдельный случай проверяет, что ответ 400 не открывает breaker, а успешный пробный вызов после паузы возвращает его в рабочее состояние. Через `AdapterDeps(clock=ManualClock())` время до пробы переводится вперёд без ожидания; сами HTTP-запросы настоящие. Проверяется переход `open → half_open → closed`, а не фактическое время восстановления инфраструктуры.

Код и тестовые серверы находятся в соседнем [практикуме с HTTP-клиентами](../2026-09-07-why-i-stopped-wrapping-http-clients/README.md); сохраните этот каталог. Проверки используют публичные метрики и серверные счётчики, а не приватное состояние breaker.

Запустите из каталога `docs/blog/lab/2026-09-07-circuit-breakers-per-origin` в копии репозитория. Версии зависимостей закреплены в `requirements.txt`.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python breakers_lab.py
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-circuit-breakers-per-origin).
