class Publication:
    def __init__(self, title, authors, info, link):
        self.title = title
        self.authors = authors
        self.info = info
        self.link = link

    def to_csv_row(self):
        return self.title + ';' + self.authors + ';' + self.info + ';' + self.link
