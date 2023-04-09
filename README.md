#### Скрипт для скачивания содержимого репотизитория по ссылке и подсчета хэша всех вложенных файлов.

_parse_script_ отличается от _parse_without_f_ наличием у первого f-строк.

**Для запуска**

```python parse_script/main.py```

Если не любите f-строки:

```python parse_without_f/main.py```

**Для проверки линтером**

```flake8 parse_script/main.py```

**Запуск тестов**

```pytest --cov-report term-missing --cov=parse_script```


