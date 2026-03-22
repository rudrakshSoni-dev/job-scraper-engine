from app.workers.celery_app import celery
from app.scrapers.indeed_scraper import IndeedScraper 
from app.db.session import SessionLocal
from app.services.job_service import bulk_create_jobs


@celery.task
def run_scraper(query: str):
    scraper = IndeedScraper()

    html = scraper.fetch(query)
    jobs = scraper.parse(html)   #directly use parsed jobs

    db = SessionLocal()
    try:
        bulk_create_jobs(db, jobs)
    finally:
        db.close()