class BaseScraper:
    def fetch(self, query: str):
        raise NotImplementedError

    def parse(self, raw):
        raise NotImplementedError

    def normalize(self, parsed):
        raise NotImplementedError