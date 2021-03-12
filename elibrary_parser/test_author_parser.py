import pytest
from bs4 import BeautifulSoup

from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.types import Publication


@pytest.fixture
def publication_table_cell():
    data_test = open('../data test/page_3.html',
                     'r', encoding= 'utf8')
    soup = BeautifulSoup(data_test, "html.parser")
    table_cells = AuthorParser.create_table_cells(soup)

    publication_table_cell = table_cells[8]

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

@pytest.fixture
def empty_string():
    table_cell = BeautifulSoup("", "html.parser")

    return table_cell


def test_get_title_with_good_data(publication_table_cell):

    assert AuthorParser.get_title(publication_table_cell) == "МЕТИЛИРОВАНИЕ ГЕНОВ МИКРОРНК ПРИ ДЕСТАБИЛИЗАЦИИ АТЕРОСКЛЕРОТИЧЕСКОЙ БЛЯШКИ"


def test_get_title_with_empty_string(empty_string):

    assert AuthorParser.get_title(empty_string) == AuthorParser.missing_value()


def test_get_authors_with_good_data(publication_table_cell):

    assert AuthorParser.get_authors(publication_table_cell) == "Марков А.В., Кучер А.Н., Назаренко М.С., Зарубин А.А., Шарыш Д.В., Барбараш О.Л., Казанцев А.Н., Бурков Н.Н., Пузырев В.П."


def test_get_authors_with_empty_string(empty_string):

    assert AuthorParser.get_authors(empty_string) == AuthorParser.missing_value()


def test_get_info_with_good_data(publication_table_cell):

    assert AuthorParser.get_info(publication_table_cell) == '''В сборнике: Молекулярная диагностика 2018. Сборник трудов Международной научно-практической конференции. 2018.  С. 102-103.'''


def test_get_info_with_empty_string(empty_string):

    assert AuthorParser.get_info(empty_string) == AuthorParser.missing_value()


def test_get_link_with_good_data(publication_table_cell):

    assert AuthorParser.get_link(publication_table_cell) == 'https://www.elibrary.ru//item.asp?id=36558133'


def test_get_link_with_empty_string(empty_string):

    assert AuthorParser.get_link(empty_string) == AuthorParser.missing_value()


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

