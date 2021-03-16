import csv
from pathlib import Path
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from elibrary_parser import config
from elibrary_parser.types import Publication


class AuthorParser:
    """Class for loading and processing publications by eLibrary authors

     Attributes
     ----------------------
     driver: WebDriver
        Firefox browser driver
        Set by method: setup_webdriver

     publications: lst
        A list with info for each author
        Set by method: save_publications

     author_id: str
        elibrary identificator

     data_path: Path
        a path where all data stored

     date_to, date_from: int
        dates (including extremities) within which search will be processed
     """
    USER_AGENTS = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Iron/28.0.1550.1 Chrome/28.0.1550.1',
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16',
    )
    DRIVER_PATH = config.DRIVER_PATH

    def __init__(self, author_id, data_path, date_to, date_from):

        self.author_id = author_id
        self.driver = None
        self.files_dir = None
        self.publications = []
        self.data_path = Path(data_path)
        self.date_to = date_to
        self.date_from = date_from

        self.create_files_dir()
        self.setup_webdriver()

    def setup_webdriver(self):
        """Settings for a selenium web driver
        Changes a self.driver attribute"""

        new_useragent = random.choice(self.USER_AGENTS)

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", new_useragent)
        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(profile, executable_path=self.DRIVER_PATH, options=options)

    def create_files_dir(self):
        """Creates directory for the web-pages of an specific author"""
        self.files_dir = self.data_path / "raw" / self.author_id

        print("Author's directory:", self.files_dir.absolute())

        self.files_dir.mkdir(exist_ok=True)

    def find_publications(self):
        """Gets the web-page with chosen years"""

        author_page_url = f'https://www.elibrary.ru/author_items.asp?authorid={self.author_id}'
        print("Author page URL:", author_page_url)

        print("Getting author's page")
        self.driver.get(author_page_url)
        print("Done")

        self.driver.find_element_by_xpath('//*[@id="hdr_years"]').click()
        time.sleep(20)

        for i in range(self.date_from, self.date_to+1):
            try:
                year = '//*[@id="year_' + str(i) + '"]'
                element = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, year)))
                self.driver.execute_script("arguments[0].click();", element)
                print('Years:', i)
            except TimeoutException:
                print("Can't load the year selection")
                print('No publications for:' + str(i) + 'year')
            except NoSuchElementException:
                print('No publications for:' + str(i) + 'year')

        # Click "search by year" button
        self.driver.find_element_by_xpath('//td[6]/div').click()  # TODO: remove hardcoded index

        page_number = 1
        is_page_real = True

        while is_page_real:
            with open(self.files_dir / f"page_{page_number}.html", 'a', encoding='utf-8') as f:
                f.write(self.driver.page_source)

            print("Downloading page number", page_number)
            page_number += 1
            
            try:
                self.driver.find_element_by_link_text('Следующая страница').click()
            except NoSuchElementException:
                is_page_real = False
                print('No more pages left!')

            sleep_seconds = random.randint(5, 15)
            print("Sleeping for", sleep_seconds, "seconds")

            time.sleep(sleep_seconds)

    @staticmethod
    def get_title(table_cell):
        """Get titles from an HTML page box
        Parameters:
        ----------------------
        table_cell : bs4.element.ResultSet
        """

        title = table_cell.find_all('span', style="line-height:1.0;")

        if not title:
            title = "-"
        else:
            title = title[0].text

        return title

    @staticmethod
    def get_authors(table_cell):
        """Get authors from an HTML page box"""

        box_of_authors = table_cell.find_all('font', color="#00008f")
        authors = box_of_authors[0].find_all('i')
        if not authors:
            authors = '-'
        else:
            authors = authors[0].text

        return authors

    @staticmethod
    def get_info(table_cell: bs4.element.ResultSet) -> str:
        """Get journal info from an HTML page box"""

        biblio_info = list(table_cell.children)[-1]
        biblio_info = biblio_info.text.strip()
        biblio_info = biblio_info.replace('\xa0', ' ')
        biblio_info = biblio_info.replace('\r\n', ' ')
        biblio_info = biblio_info.replace('\n', ' ')

        return biblio_info

    @staticmethod
    def get_link(table_cell: bs4.element.ResultSet) -> str:
        """Get article link from an HTML page box"""

        links_in_box = table_cell.find_all('a')

        links = []
        for link in links_in_box:
            links.append(link.get('href'))
        paper_link = 'https://www.elibrary.ru/' + links[0]  # TODO: check if it's always a paper link

        return paper_link

    def save_publications(self):
        """Save author's publications to a csv-file"""

        save_path = self.data_path / "processed" / self.author_id
        save_path.mkdir(exist_ok=True)

        csv_path = save_path / "publications.csv"

        with open(csv_path, 'a', encoding="utf8", newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=';')
            for publication in self.publications:
                saving_publication = [
                    publication.title,
                    publication.authors,
                    publication.info,
                    publication.link,
                    publication.year
                ]
                wr.writerow(saving_publication)

    def parse_publications(self):
        """ Get trough the html file and save information from it"""

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
                info = self.get_info(table_cell)

                publication = Publication(
                    title=self.get_title(table_cell),
                    authors=self.get_authors(table_cell),
                    info=info,
                    link=self.get_link(table_cell),
                )
                publication.get_year()

                self.publications.append(publication)
