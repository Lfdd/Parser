from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import save_common_publications
from pathlib import Path


author_ids = ["679517"]
# "638022""108193"
publications = []
data_path = "C://Users//SZ//PycharmProjects//Parser//data"
date_from = 2018
date_to = 2020


for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path="C://Users//SZ//PycharmProjects//Parser//data",
        date_from=date_from,
        date_to=date_to
    )

    parser.find_publications()  # Загрузка HTML-файлов с публикациями
    parser.parse_publications()  # Извлечение информации из HTML-файлов
    parser.save_publications()  # Сохранение информации в CSV-файл

    publications.append(set(parser.publications))

    save_common_publications(data_path=Path(data_path), date_from=date_from, date_to=date_to, publications=publications)
