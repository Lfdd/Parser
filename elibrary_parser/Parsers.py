from pathlib import Path
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from elibrary_parser.types import Publication


class AuthorParser:
    USER_AGENTS = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Iron/28.0.1550.1 Chrome/28.0.1550.1',
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16',
    )
    DRIVER_PATH = "D:\\Software\\geckodriver.exe"  # TODO: generalize it
   

    def __init__(self, author_id, data_path):
        self.author_id = author_id
        self.driver = None
        self.files_dir = None
        self.publications = []
        self.data_path = Path(data_path)

        self.create_files_dir()
        self.setup_webdriver()

    def setup_webdriver(self):
        new_useragent = random.choice(self.USER_AGENTS)

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", new_useragent)
        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(profile, executable_path=self.DRIVER_PATH, options=options)

    def create_files_dir(self):
        """Creates directory for the web-pages of an specific author

        """
        self.files_dir = self.data_path / "raw" / self.author_id

        print("Author's directory:", self.files_dir.absolute())

        self.files_dir.mkdir(exist_ok=True)

    def find_publications(self):
        """Gets the web-page
        Cycle 'while' creates "page.html" in "files_dir"
        Trying to get the next page by using "find_element_by_xpath"
        Sleeps for a few seconds in order to load properly
        While there is no specific error "NoSuchElementException"
        Which means that no page was loaded. If so stops

        Raises
        ------
        NoSuchElementException
            Means that there is no element defined by xpath.

        """

        author_page_url = f'https://www.elibrary.ru/author_items.asp?authorid={self.author_id}'
        print("Author page URL:", author_page_url)

        print("Getting author's page")
        self.driver.get(author_page_url)
        print("Done")

        is_page_real = True
        page_number = 1

        while is_page_real:
            with open(self.files_dir / f"page_{page_number}.html", 'a', encoding='utf-8') as f:
                f.write(self.driver.page_source)

            print("Downloading page number", page_number)
            page_number = page_number + 1

            try:
                  self.driver.find_element_by_link_text('Следующая страница').click()
            except NoSuchElementException:
                is_page_real = False
                print('Больше нет страниц!')

            sleep_seconds = random.randint(5, 15)
            print("Sleeping for", sleep_seconds, "seconds")

            time.sleep(sleep_seconds)

    def get_title(self, table_cell):
        title = table_cell.find_all('span', style="line-height:1.0;")

        if not title:
            title = "-"
        else:
            title = title[0].text

        return title

    def get_authors(self, table_cell):
        box_of_authors = table_cell.find_all('font', color="#00008f")
        authors = box_of_authors[0].find_all('i')
        if not authors:
            authors = '-'
        else:
            authors = authors[0].text

        return authors

    def get_info(self, table_cell):
        biblio_info = list(table_cell.children)[-1]
        biblio_info = biblio_info.text.strip()
        biblio_info = biblio_info.replace('\xa0', ' ')
        biblio_info = biblio_info.replace('\r\n', ' ')
        biblio_info = biblio_info.replace('\n', ' ')

        return biblio_info

    def get_link(self, table_cell):
        links_in_box = table_cell.find_all('a')

        links = []
        for link in links_in_box:
            links.append(link.get('href'))
        paper_link = 'https://www.elibrary.ru/' + links[0]  # TODO: check if it's always a paper link

        return paper_link

    def save_publications(self):
        save_path = self.data_path / "processed" / self.author_id
        save_path.mkdir(exist_ok=True)

        csv_path = save_path / "publications.csv"

        with open(csv_path, 'a', encoding="utf8", newline='') as csvfile:
            for publication in self.publications:
                csvfile.write(publication.to_csv_row() + "\n")

    def parse_publications(self):
        print("Parsing publications for author", self.author_id)

        for file in self.files_dir.glob("*.html"):
            print("Reading file", file.name)

            with open(file, "r", encoding="utf8") as f:
                page_text = f.read()

            soup = BeautifulSoup(page_text, "html.parser")
            publications_table = soup.find_all('table', id="restab")[0]

            rubbish = publications_table.find_all('table', width="100%", cellspacing="0")
            for box in rubbish:
                box.decompose()  # Remove all inner tags

            table_cells = publications_table.find_all('td', align="left", valign="top")

            print("LENGTH OF INFO", len(table_cells))

            for table_cell in table_cells:
                title = self.get_title(table_cell)
                authors = self.get_authors(table_cell)
                info = self.get_info(table_cell)
                link = self.get_link(table_cell)

                self.publications.append(
                    Publication(
                        title=title,
                        authors=authors,
                        info=info,
                        link=link
                    )
                )
