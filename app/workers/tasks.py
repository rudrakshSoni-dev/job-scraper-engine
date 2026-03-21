from app.workers.celery_app import celery
from app.db.session import SessionLocal
from app.services.job_service import create_job


@celery.task
def process_job(data: dict):
    db = SessionLocal()
    try:
        print("Processing:", data)
        create_job(db, data)
    finally:
        db.close()