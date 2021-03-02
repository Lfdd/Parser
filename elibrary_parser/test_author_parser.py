import pytest
from bs4 import BeautifulSoup

from elibrary_parser.Parsers import AuthorParser


@pytest.fixture
def publication_table_cell():
    return """<td valign="top" align="left">
    <a href="/item.asp?id=36832133"><b><span style="line-height:1.0;">ИССЛЕДОВАНИЕ ЧИСЛА КОПИЙ МТДНК НА КЛЕТКУ ПРИ АТЕРОСКЛЕРОЗЕ</span></b></a><br><font color="#00008f"><i>Салахов Р.Р., Голубенко М.В., Марков А.В., Слепцов А.А., Назаренко М.С.</i></font><br>
    <font color="#00008f">
     В сборнике: Актуальные вопросы фундаментальной и клинической медицины.&nbsp;Сборник материалов конгресса молодых ученых. Под редакцией Е.Л. Чойнзонова. 2018.  С. 126-128.
    </font></td>"""


def test_get_title_with_good_data(publication_table_cell):
    table_cell = BeautifulSoup(publication_table_cell, "html.parser")

    assert AuthorParser.get_title(table_cell) == "ИССЛЕДОВАНИЕ ЧИСЛА КОПИЙ МТДНК НА КЛЕТКУ ПРИ АТЕРОСКЛЕРОЗЕ"


def test_get_title_with_empty_string():
    table_cell = BeautifulSoup("", "html.parser")

    assert AuthorParser.get_title(table_cell) == "-"
