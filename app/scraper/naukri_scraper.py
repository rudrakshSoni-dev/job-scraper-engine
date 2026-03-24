# app/scraper/naukri_scraper.py

import requests
from bs4 import BeautifulSoup
from app.scraper.base import BaseScraper

import logging

logger = logging.getLogger(__name__)


class NaukriScraper(BaseScraper):

    BASE_URL = "https://www.naukri.com/jobs-in-{location}?k={query}"

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    def scrape_jobs(self, query: str, location: str) -> list[dict]:
        try:
            url = self._build_url(query, location)
            logger.info(f"[Naukri] URL: {url}")

            res = requests.get(url, headers=self.HEADERS, timeout=10)

            if res.status_code != 200:
                logger.warning(f"[Naukri] Bad response: {res.status_code}")
                return []

            return self._parse(res.text, query, location)

        except Exception as e:
            logger.error(f"[Naukri] Failed: {e}")
            return []

    def _build_url(self, query, location):
        query = query.replace(" ", "-")
        location = location.replace(" ", "-")

        return self.BASE_URL.format(query=query, location=location)

    def _parse(self, html, query, location):
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        cards = soup.select("article.jobTuple")

        logger.info(f"[Naukri] Cards found: {len(cards)}")

        for card in cards:
            try:
                title = card.select_one("a.title")
                company = card.select_one("a.subTitle")
                loc = card.select_one(".locWdth")
                link = title["href"] if title else None

                if not title or not company:
                    continue

                jobs.append({
                    "title": title.text.strip(),
                    "company": company.text.strip(),
                    "location": loc.text.strip() if loc else location,
                    "url": link,
                    "source": "naukri",
                    "query": query
                })

            except Exception as e:
                logger.warning(f"[Naukri] Parse error: {e}")
                continue

        return jobs