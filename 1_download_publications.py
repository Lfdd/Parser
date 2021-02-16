from elibrary_parser.Parsers import AuthorParser

AUTHOR_ID = "679517"

parser = AuthorParser(author_id=AUTHOR_ID)
parser.find_publications()
