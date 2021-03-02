import re


class Publication:
    def __init__(self, title, authors, info, link, year):
        self.title = title
        self.authors = authors
        self.info = info
        self.link = link
        self.year = year

    def to_csv_row(self):
        return self.title + ';' + self.authors + ';' + self.info + ';' + self.link + ';' self.year

    #def get_year(self):
     #   years = re.findall(r'20\d{​​2}​​|19\d{​​2}​​', self.info)

      #  if years:
       #     self.year = years[0]

    def __eq__(self, other):
        return (
                self.title == other.title
                and self.authors == other.authors
                and self.info == other.info
                and self.link == other.link
                and self.year == other.year
        )

    def __hash__(self):
        return hash(self.title) ^ hash(self.authors) ^ hash(self.info) ^ hash(self.link) ^ hash(self.year)
