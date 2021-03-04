import pytest
from bs4 import BeautifulSoup

from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.types import Publication


@pytest.fixture
def publication_table_cell():
    data_test = open('C:/Users/Иван Заваруев/PycharmProjects/Parser/data/raw/679517/page_3.html',
                     'r', encoding= 'utf8')
    soup = BeautifulSoup(data_test, "html.parser")
    publications_table = soup.find_all('table', id="restab")[0]

    rubbish = publications_table.find_all('table', width="100%", cellspacing="0")
    for box in rubbish:
        box.decompose()  # Remove all inner tags

    table_cells = publications_table.find_all('td', align="left", valign="top")

    publication_table_cell = table_cells[3]

    #<td align="left" valign="top">
    #<a href="/item.asp?id=36558133"><b><span style="line-height:1.0;">
    #МЕТИЛИРОВАНИЕ ГЕНОВ МИКРОРНК ПРИ ДЕСТАБИЛИЗАЦИИ АТЕРОСКЛЕРОТИЧЕСКОЙ БЛЯШКИ</span></b></a>
    #<br/><font color="#00008f"><i>Марков А.В., Кучер А.Н., Назаренко М.С., Зарубин А.А., Шарыш Д.В.,
    # Барбараш О.Л., Казанцев А.Н., Бурков Н.Н., Пузырев В.П.</i></font><br/>
    #<font color="#00008f">
    #В сборнике: Молекулярная диагностика 2018.
    # Сборник трудов Международной научно-практической конференции. 2018.  С. 102-103.
    #</font></td>

    return publication_table_cell


def test_get_title_with_good_data(publication_table_cell):

    assert AuthorParser.get_title(publication_table_cell) == "МЕТИЛИРОВАНИЕ ГЕНОВ МИКРОРНК ПРИ ДЕСТАБИЛИЗАЦИИ АТЕРОСКЛЕРОТИЧЕСКОЙ БЛЯШКИ"


def test_get_title_with_empty_string():
    table_cell = BeautifulSoup("", "html.parser")

    assert AuthorParser.get_title(table_cell) == "-"


def test_get_authors_with_good_data(publication_table_cell):

    assert AuthorParser.get_authors(publication_table_cell) == "Марков А.В., Кучер А.Н., Назаренко М.С., Зарубин А.А., Шарыш Д.В., Барбараш О.Л., Казанцев А.Н., Бурков Н.Н., Пузырев В.П."


def test_get_authors_with_empty_string():
    table_cell = BeautifulSoup("", "html.parser")

    assert AuthorParser.get_authors(table_cell) == "-"


def test_get_info_with_good_data(publication_table_cell):

    assert AuthorParser.get_info(publication_table_cell) == '''В сборнике: Молекулярная диагностика 2018. Сборник трудов Международной научно-практической конференции. 2018.  С. 102-103.'''


def test_get_info_with_empty_string():
    table_cell = BeautifulSoup("", "html.parser")

    assert AuthorParser.get_info(table_cell) == "-"


def test_get_link_with_good_data(publication_table_cell):

    assert AuthorParser.get_link(publication_table_cell) == 'https://www.elibrary.ru//item.asp?id=36558133'


def test_get_link_with_empty_string():
    table_cell = BeautifulSoup("", "html.parser")

    assert AuthorParser.get_link(table_cell) == "-"


def test_get_year_with_good_data(publication_table_cell):
    info = AuthorParser.get_info(publication_table_cell)
    publication = Publication(title='', authors='', info=info, link='')
    publication.get_year()

    assert publication.year == '2018'


def test_get_year_with_info_without_year():
    info = 'В сборнике: Молекулярная диагностика. Сборник трудов Международной научно-практической конференции. С. 102-103.'

    publication = Publication(title='', authors='', info=info, link='')
    publication.get_year()

    assert publication.year == '-'

