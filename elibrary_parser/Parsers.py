from pathlib import Path
import random
import time

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
    DATA_PATH = Path("C:/Users/vladi/PycharmProjects/Parser/data/raw")  # TODO: generalize it

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
        self.files_dir = self.DATA_PATH / self.author_id

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
