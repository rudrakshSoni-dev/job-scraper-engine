from app.core.celery_app import celery_app
from app.scraper.playwright_scraper import PlaywrightScraper
from app.utils.hash import generate_job_hash
from app.db.crud.job_crud import bulk_insert_jobs
from app.db.session import SessionLocal

import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3}
)
def scrape_jobs_task(self, payload: dict):
    query = payload.get("query")
    location = payload.get("location")

    if not query or not location:
        raise ValueError("query and location are required")

    scraper = PlaywrightScraper()

    jobs = scraper.scrape_jobs(query, location)
    logger.info(f"Scraped {len(jobs)} jobs for {query} - {location}")

    processed_jobs = []
    for job in jobs:
        try:
            job["source"] = "indeed"
            job["hash"] = generate_job_hash(job)
            job["query"] = query.strip().lower()
            job["location"] = job.get("location", "").strip().lower()

            processed_jobs.append(job)
        except Exception as e:
            logger.warning(f"Skipping job due to error: {e}")
            continue

    db = SessionLocal()
    try:
        inserted = bulk_insert_jobs(db, processed_jobs)
    except Exception as e:
        logger.error(f"DB insert failed: {e}")
        raise
    finally:
        db.close()

    return {
        "status": "stored",
        "inserted": inserted,
        "scraped": len(processed_jobs)
    }