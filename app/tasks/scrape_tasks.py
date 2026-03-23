from app.core.celery_app import celery_app
from app.scraper.playwright_scraper import PlaywrightScraper

@celery_app.task(bind=True)
def scrape_jobs_task(self, payload: dict):
    scraper = PlaywrightScraper()

    jobs = scraper.scrape_jobs(
        payload["query"],
        payload["location"]
    )

    return jobs