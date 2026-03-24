# app/tasks/source_tasks.py

from app.core.celery_app import celery_app
from app.scraper.playwright_scraper import PlaywrightScraper
from app.scraper.naukri_scraper import NaukriScraper
from app.db.session import SessionLocal
from app.db.crud.job_crud import bulk_insert_jobs
from app.utils.hash import generate_job_hash
from app.services.freshness import update_freshness
from app.services.lock import lock_key, release_lock
from app.core.redis_client import redis_client

import logging

logger = logging.getLogger(__name__)


def process_and_store(jobs, query, location):
    processed = []

    for job in jobs:
        try:
            job["hash"] = generate_job_hash(job)
            job["query"] = query
            job["location"] = job.get("location", "").strip().lower()
            processed.append(job)
        except:
            continue

    db = SessionLocal()
    try:
        inserted = bulk_insert_jobs(db, processed)
        update_freshness(db, query, location)
        return inserted
    finally:
        db.close()


@celery_app.task
def scrape_indeed_task(query, location):
    scraper = PlaywrightScraper()

    try:
        jobs = scraper.scrape_jobs(query, location)
        return process_and_store(jobs, query, location)
    except Exception as e:
        logger.error(f"Indeed failed: {e}")
        return 0


@celery_app.task
def scrape_naukri_task(query, location):
    scraper = NaukriScraper()

    try:
        jobs = scraper.scrape_jobs(query, location)
        return process_and_store(jobs, query, location)
    except Exception as e:
        logger.error(f"Naukri failed: {e}")
        return 0