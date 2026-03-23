import requests

class TestScraper:
    def fetch(self, query):
        return [
            {
                "title": f"{query} Engineer",
                "company": "TestCompany",
                "location": "Remote",
                "source": "test",
                "url": "example.com"
            }
        ]
    
    def parse(self, raw):
        return raw

    def normalize(self, parsed):
        return parsed