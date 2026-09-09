# Практикум: стоимость установки и импорта библиотеки {#lab-what-a-library-costs-to-install-and-to-import}

Для каждой из восьми библиотек создаётся чистое виртуальное окружение, устанавливается базовый пакет, подсчитываются установленные дистрибутивы и объём на диске, а также выбирается лучшее время импорта корневого модуля из пяти запусков. Затем измерения повторяются с одним extra: разница показывает его стоимость. В конце проверяется сообщение при обращении к функции, для которой нужный extra не установлен.

```bash
uv venv --python 3.13 .venv
.venv/bin/python footprint.py       # it creates its own throwaway venv per package
```

[Исходный код практикума на GitHub](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-zero-dependency-cores).
