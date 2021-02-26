class Publication:
    def __init__(self, title, authors, info, link):
        self.title = title
        self.authors = authors
        self.info = info
        self.link = link

    def to_csv_row(self):
        return self.title + ';' + self.authors + ';' + self.info + ';' + self.link

    def __eq__(self, other):
        return (
                self.title == other.title
                and self.authors == other.authors
                and self.info == other.info
                and self.link == other.link
        )

    def __hash__(self):
        return hash(self.title) ^ hash(self.authors) ^ hash(self.info) ^ hash(self.link)
