from app.core.celery_app import celery_app
from app.scraper.playwright_scraper import PlaywrightScraper
from app.db.crud.job_crud import bulk_upsert_jobs
from app.db.session import SessionLocal

import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3}
)
def scrape_jobs_task(self):
    """
    NEW:
    - No payload
    - Runs scheduled
    - Scrapes predefined queries
    """

    scraper = PlaywrightScraper()
    db = SessionLocal()

    try:
        # scrape (no inputs)
        jobs = scraper.scrape_jobs()

        logger.info(f"Scraped {len(jobs)} jobs")

        if not jobs:
            return {"status": "no_data"}

        # ensure required fields
        processed_jobs = []
        for job in jobs:
            try:
                if not job.get("external_id"):
                    continue

                job["source"] = job.get("source", "indeed")

                processed_jobs.append(job)

            except Exception as e:
                logger.warning(f"Skipping job: {e}")

        # UPSERT (NOT insert)
        inserted = bulk_upsert_jobs(db, processed_jobs)

        return {
            "status": "stored",
            "upserted": inserted,
            "total": len(processed_jobs)
        }

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise

    finally:
        db.close()