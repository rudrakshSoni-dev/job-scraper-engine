from app.core.celery_app import celery_app
from app.scraper.playwright_scraper import PlaywrightScraper
from app.utils.hash import generate_job_hash
from app.db.crud.job_crud import bulk_insert_jobs
from app.db.session import SessionLocal
from app.services.freshness import update_freshness
from app.services.lock import lock_key, release_lock  #FIXED
from app.core.redis_client import redis_client

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

    # normalize once
    query = query.strip().lower()
    location = location.strip().lower()

    key = lock_key(query, location)

    scraper = PlaywrightScraper()
    db = SessionLocal()

    try:
        # scrape
        jobs = scraper.scrape_jobs(query, location)
        logger.info(f"Scraped {len(jobs)} jobs for {query} - {location}")

        # process
        processed_jobs = []
        for job in jobs:
            try:
                job["source"] = "indeed"
                job["hash"] = generate_job_hash(job)
                job["query"] = query
                job["location"] = job.get("location", "").strip().lower()

                processed_jobs.append(job)
            except Exception as e:
                logger.warning(f"Skipping job due to error: {e}")
                continue

        # insert
        inserted = bulk_insert_jobs(db, processed_jobs)

        # update freshness ONLY after success
        update_freshness(db, query, location)

        return {
            "status": "stored",
            "inserted": inserted,
            "scraped": len(processed_jobs)
        }

    except Exception as e:
        logger.error(f"Scraping pipeline failed: {e}")
        raise

    finally:
        # ✅ ALWAYS release lock (via service)
        try:
            release_lock(redis_client, key)
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")

        db.close()