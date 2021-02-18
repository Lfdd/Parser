import csv
from pathlib import Path
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


class AuthorParser:
    USER_AGENTS = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Iron/28.0.1550.1 Chrome/28.0.1550.1',
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16',
    )
    DRIVER_PATH = "D:\\Software\\geckodriver.exe"  # TODO: generalize it
    NEXT_PAGE_LINK = '/html/body/div[3]/table/tbody/tr/td/table[1]/tbody/tr/td[2]/form/table/tbody/tr[2]/td[1]/table/tbody/tr/td/div[4]/table/tbody/tr/td[10]/a'
    DATA_PATH = Path("C:/Users/vladi/PycharmProjects/Parser/data/")  # TODO: generalize it

    def __init__(self, author_id):
        self.author_id = author_id
        self.driver = None
        self.files_dir = None

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
        self.files_dir = self.DATA_PATH / "raw" / self.author_id

        print("Author's directory:", self.files_dir.absolute())

        self.files_dir.mkdir(exist_ok=True)

    def find_publications(self):
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
                self.driver.find_element_by_xpath(self.NEXT_PAGE_LINK).click()
            except NoSuchElementException:
                is_page_real = False
                print('Больше нет страниц!')

            sleep_seconds = random.randint(5, 15)
            print("Sleeping for", sleep_seconds, "seconds")

            time.sleep(sleep_seconds)

    def get_titles(self, soup):
        title = soup.find_all('span', style="line-height:1.0;")
        titles = []
        for i in title:
            titles.append(i.text)

        return titles

    def get_authors(self, info):
        authors_to_save = []

        for i in range(len(info)):
            if len(info[i]) > 5:  # Check if authors exist
                authors = info[i].find_all('i')
                for author in authors:
                    authors_to_save.append(author.text)
            else:
                authors_to_save.append('-')

        return authors_to_save

    def get_information(self, info):
        info_save = []
        for info_block in info:
            publication_information = list(info_block.children)[-1]

            if publication_information is None:
                information_text = ""
            else:
                information_text = publication_information.text.strip()
                information_text = information_text.replace('\xa0', ' ')  # Delete weird symbols
                information_text = information_text.replace('\r\n', ' ')  # Delete rows splits
                information_text = information_text.replace('\n', ' ')  # Delete rows splits
            info_save.append(information_text)

        return info_save

    def get_links(self, info):
        links = []
        for info_block in info:
            all_links = []
            link = info_block.find_all('a')
            for j in link:  # TODO: check if it is always a list?
                all_links.append(j.get('href'))
            if all_links:
                links.append('https://www.elibrary.ru/' + all_links[0])
            else:
                links.append("")

        return links

    def save_publications(self, titles, authors, informations, links):
        save_path = self.DATA_PATH / "processed" / self.author_id
        save_path.mkdir(exist_ok=True)

        csv_path = save_path / "publications.csv"

        with open(csv_path, 'a', encoding="utf8", newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=';')
            for i in range(len(titles)):
                article = [titles[i], authors[i], informations[i], links[i]]
                wr.writerow(article)

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

            info = publications_table.find_all('td', align="left", valign="top")

            titles = self.get_titles(soup)
            authors = self.get_authors(info)
            informations = self.get_information(info)
            links = self.get_links(info)

            self.save_publications(titles, authors, informations, links)
