# Парсер научных журналов eLibrary

Краткое описание
----------------

Данная программа собирает список публикаций автора по его идентификатору eLibrary и информацию о статьях. В текущей версии сохраняется следующая информация:
* Заголовок публикации (title), 
* Список авторов (authors), 
* Библиографическая информация (info), 
* Ссылка на страницу публикации (link). 

HTML-страницы с публикациями автора загружаются в папку `<data_path>/raw/<author_id>`. Информация о публикациях сохраняется в файл формата CSV в папку `<data_path>/processed/<author_id>/publications.csv`. 

Также программа может находить общие публикации коллектива авторов.

Пример работы:

```python
from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications


author_ids = ["1","2","3"]
publications = []

for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path="C://Parser/data/",
        date_from=1984, 
        date_to=2021 
    )

    parser.find_publications()  # Загрузка HTML-файлов с публикациями
    parser.parse_publications()  # Извлечение информации из HTML-файлов
    parser.save_publications()  # Сохранение информации в CSV-файл

    publications.append(set(parser.publications))

# Поиск общих публикаций коллектива авторов
common_publications = find_common_publications(publications)
print("Found", len(common_publications), "common publications")

# Вывод названия и авторов общих публикаций
for publication in common_publications:
    print(publication.title)
    print(publication.authors)
    print("-" * 20)

```

Установка
---------

Вам потребуется Python 3.5 или более поздней версии. Вы можете иметь несколько установленных версий, это не должно вызвать проблем.

Также для корректной работы Вам подребуется установить некоторые библиотеки. Для этого можно просто указать путь до requirements.txt в консоли и ввести команду.

```bash
$ pip install -r /path/to/requirements.txt
```
Чтобы библиотека selenium могла имитировать работу браузера необходимо иметь предустановленным браузер [Firefox](https://www.mozilla.org/en-US/firefox/new/), а также [gekodriver.exe](https://github.com/mozilla/geckodriver/releases), затем указать в файле [config.py](elibrary_parser/config.py) путь до gekodriver на Вашем компьютере.
