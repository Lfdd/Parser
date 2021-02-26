from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications

author_ids = [
    "679517",  # Марков
    "108193",  # Пузырёв
    "638022"  # Слепцов
]

publications = []

for author_id in author_ids:
    parser = AuthorParser(author_id=author_id, data_path="C:/Users/vladi/PycharmProjects/Parser/data/")
    # parser.find_publications()
    parser.parse_publications()
    parser.save_publications()

    publications.append(set(parser.publications))

for author_publications in publications:
    for publication in author_publications:
        print(publication.title)
        print(publication.authors)
        print("-"*20)
        print()


common_publications = find_common_publications(publications)
print("Found", len(common_publications), "common publications")

for publication in common_publications:
    print(publication.title)
    print(publication.authors)
    print("-"*20)
