from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.job import Job
import hashlib


def generate_hash(job):
    key = f"{job['title']}-{job['company']}-{job.get('location')}"
    return hashlib.sha256(key.encode()).hexdigest()


def create_job(db: Session, data: dict):
    data["hash"] = generate_hash(data)

    job = Job(**data)
    db.add(job)

    try:
        db.commit()
        db.refresh(job)
        return job

    except IntegrityError:  # dedup via UNIQUE(hash)
        db.rollback()
        return None