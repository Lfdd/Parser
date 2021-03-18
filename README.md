# Парсер научных журналов eLibrary

Краткое описание
-------------

Данная программа собирает список публикаций автора по его идентификатору 
(author_id) и информацию о статьях, где: 
заголовок (title), 
список авторов (authors), 
литературное издание (info), 
а также ссылку на страницу публикации (link). 
Затем загружает HTML-страницы с публикациями автора в /data/raw/(author_id), 
извлекает информацию и сохраняет её в табличном формате в файл формата csv в папке 
/data/processed/(author_id), а также находит общие публикации коллектива авторов.

Пример работы с программой:

```python
from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications

author_ids = ["1","2","3"]
for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path="C://Parser/data/",
        date_from=1984, 
        date_to=2021 

parser.find_publications()
parser.parse_publications()
parser.save_publications()

publications.append(set(parser.publications))

common_publications = find_common_publications(publications)
for publication in common_publications: #Выводит название и авторов общих публикаций
    print(publication.title)
    print(publication.authors)
    )
```

Установка
------------

Вам потребуется Python 3.5 или более поздней версии. Вы можете иметь 
несколько установленных версий, это не должно вызвать проблем.

Также для корректной работы Вам подребуется установить некоторые библиотеки.
Для этого можно просто указать путь до requirments.txt в консоли и ввести команду.

```python
pip install -r /path/to/requirements.txt
```
Чтобы библиотека selenium могла имитировать работу браузера необходимо иметь предустановленным
браузер [Firefox](https://www.mozilla.org/en-US/firefox/new/), а также [gekodriver.exe](https://github.com/mozilla/geckodriver/releases), 
затем указать в /elibrary_parser/config.py путь до gekodriver.exe на Вашем 
компьютере.
