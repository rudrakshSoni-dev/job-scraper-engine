from celery import shared_task
from scraper.playwright_scraper import PlaywrightScraper
from app.services.job_service import save_jobs

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def scrape_jobs_task(self, payload: dict):
    scraper = PlaywrightScraper()

    jobs = scraper.scrape_jobs(
        payload["query"],
        payload["location"]
    )

    save_jobs(jobs)

    return jobs