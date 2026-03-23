from celery import shared_task
from scraper.playwright_scraper import PlaywrightScraper
from app.services.job_service import bulk_insert_jobs
import logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def scrape_jobs_task(self, query, location):
    scraper = PlaywrightScraper()

    try:
        scraper.start()
        jobs = scraper.scrape_jobs(query, location)

        logger.info(f"Scraped {len(jobs)} jobs for query='{query}' location='{location}'")

        bulk_insert_jobs(jobs)

        logger.info("DB insert completely")
        # normalize + hash inside service
        bulk_insert_jobs(jobs)

        return {"count": len(jobs)}

    finally:
        scraper.stop()