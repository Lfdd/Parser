from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications


author_ids = ["679517","108193","638022"]
publications = []

for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path="C://Users//SZ//PycharmProjects//Parser//data",
        date_from=2017,
        date_to=2020
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