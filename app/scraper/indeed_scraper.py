import requests
from bs4 import BeautifulSoup



class IndeedScraper:
    BASE_URL = "https://www.indeed.com/jobs"

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    def fetch(self, query):
        params = {"q": query, "l": "Remote"}
        res = requests.get(
            self.BASE_URL,
            params=params,
            headers=self.HEADERS,
            timeout=10
        )
        return res.text

    # ✅ THIS METHOD MUST EXIST INSIDE CLASS
    def parse(self, html):
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        cards = soup.select("div.job_seen_beacon, div.cardOutline")
        print("CARDS FOUND:", len(cards))

        for card in cards:
            title = card.select_one("h2 a span") or card.select_one("h2 span")
            company = card.select_one(".companyName")
            location = card.select_one(".companyLocation")
            link = card.select_one("h2 a")

            if not title or not company:
                continue

            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location.text.strip() if location else None,
                "url": "https://indeed.com" + link["href"] if link else None,
                "source": "indeed"
            })

        print("JOBS FOUND:", len(jobs))
        return jobs