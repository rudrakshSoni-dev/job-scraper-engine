# app/scraper/factory.py

from app.scraper.playwright_scraper import PlaywrightScraper
from app.scraper.naukri_scraper import NaukriScraper


def get_scrapers():
    return [
        PlaywrightScraper(),  # primary
        NaukriScraper(),      # new source
    ]