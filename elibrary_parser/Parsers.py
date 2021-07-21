import csv
from pathlib import Path
import random
import time
import bs4

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from elibrary_parser import config
from elibrary_parser.types import Publication
from elibrary_parser.secrets import Secrets


class AuthorParser:
    """Class for loading and processing publications by eLibrary authors

     Attributes
     -----------
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
    USER_AGENTs_list = []
    with open('../user_agent.txt', 'r', encoding='UTF-8') as ua:
        for line in ua:
            line = line.strip()
            USER_AGENTs_list.append(line)
    used_useragent = random.choice(USER_AGENTs_list)

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
        self.setup_webdriver(new_useragent=self.used_useragent)

    missing_value = '-'

    def setup_webdriver(self, new_useragent):
        """Settings for a selenium web driver
        Changes a self.driver attribute"""

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", new_useragent)
        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(profile, executable_path=self.DRIVER_PATH, options=options)

    def create_files_dir(self):
        """Creates directory for the web-pages of an specific author"""
        raw_data_dir = self.data_path / "raw"
        raw_data_dir.mkdir(exist_ok=True)

        processed_data_dir = self.data_path / "processed"
        processed_data_dir.mkdir(exist_ok=True)

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
        return page_number

    def authorization(self):
        author_page_url = f'https://www.elibrary.ru/author_items.asp?authorid={self.author_id}'
        print("Author page URL:", author_page_url)

        print("Getting author's page")
        self.driver.get(author_page_url)
        print("Done")

        login = self.driver.find_element_by_id('login')
        login.send_keys(Secrets.elib_login)
        time.sleep(10)

        password = self.driver.find_element_by_id('password')
        password.send_keys(Secrets.elib_password)
        password.send_keys(Keys.RETURN)
        time.sleep(10)

    def download_page_of_publications(self, page_number):
        """Gets the web-page of the author's publications"""
        request_number = page_number

        for publication in self.publications:
            link_of_page = publication.link
            print('getting publication page')
            self.driver.get(link_of_page)
            print('Done')

            page_id = link_of_page.split('=')
            page_id = page_id[1]

            publication_data_dir = self.files_dir/'publications'
            publication_data_dir.mkdir(exist_ok=True)

            with open(publication_data_dir/f'{page_id}.html', 'a', encoding='utf-8') as f:
                f.write(self.driver.page_source)

            print("Downloading page number", request_number)
            request_number += 1

            if request_number % 90 == 0:
                previous_user_agent = self.used_useragent
                self.used_useragent = random.choice(self.USER_AGENTs_list)
                while previous_user_agent == self.used_useragent:
                    self.used_useragent = random.choice(self.USER_AGENTs_list)
                self.setup_webdriver(new_useragent=self.used_useragent)

            sleep_seconds = random.randint(3, 7)
            print("Sleeping for", sleep_seconds, "seconds")

            time.sleep(sleep_seconds)

    @staticmethod
    def get_title(table_cell: bs4.element.ResultSet) -> str:
        """Get publication titles from an HTML page box

        Parameters:
        -----------
        table_cell : bs4.element.ResultSet
        """

        title = table_cell.find_all('span', style="line-height:1.0;")

        if not title:
            title = AuthorParser.missing_value
        else:
            title = title[0].text

        return title

    @staticmethod
    def get_authors(table_cell: bs4.element.ResultSet) -> str:
        """Get authors from an HTML page box"""

        box_of_authors = table_cell.find_all('font', color="#00008f")
        if not box_of_authors:
            authors = AuthorParser.missing_value
        else:
            authors = box_of_authors[0].find_all('i')
            if not authors:
                authors = AuthorParser.missing_value
            else:
                authors = authors[0].text

        return authors

    @staticmethod
    def get_info(table_cell: bs4.element.ResultSet) -> str:
        """Get journal info from an HTML page box"""

        if len(table_cell) == 0:
            biblio_info = AuthorParser.missing_value
        else:
            biblio_info = list(table_cell.children)[-1]
            biblio_info = biblio_info.text.strip()
            biblio_info = biblio_info.replace('\xa0', ' ')
            biblio_info = biblio_info.replace('\r\n', ' ')
            biblio_info = biblio_info.replace('\n', ' ')

        return biblio_info

    @staticmethod
    def get_link(table_cell: bs4.element.ResultSet) -> str:
        """Get article link from an HTML page box"""

        information_wint_links_in_box = table_cell.find_all('a')
        if not information_wint_links_in_box:
            paper_link = AuthorParser.missing_value
        else:
            title_information_with_link = information_wint_links_in_box[0]
            link = title_information_with_link.get('href')
            paper_link = 'https://www.elibrary.ru/' + link  # TODO: check if it's always a paper link

        return paper_link

    @staticmethod
    def create_table_cells(soup):
        publications_table = soup.find_all('table', id="restab")[0]

        rubbish = publications_table.find_all('table', width="100%", cellspacing="0")
        for box in rubbish:
            box.decompose()  # Remove all inner tags

        table_cells = publications_table.find_all('td', align="left", valign="top")

        return table_cells

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

            table_cells = self.create_table_cells(soup)

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
