import json
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.job import Job
from app.core.redis_client import redis_client


# -------------------------
# CACHE KEY
# -------------------------
def cache_key(query: str, location: str) -> str:
    return f"jobs:{query}:{location}"
# -------------------------
# GET JOBS (CACHE + DB)
# -------------------------
def get_jobs(query: str, location: str):
    key = cache_key(query, location)

    # ✅ 1. Try cache
    cached = redis_client.get(key)
    if cached:
        return {
            "source": "cache",
            "data": json.loads(cached)
        }

    # ✅ 2. DB fallback
    db: Session = SessionLocal()
    try:
        jobs = db.query(Job).filter(
            Job.query == query,
            Job.location == location
        ).order_by(Job.created_at.desc()).limit(50).all()

        serialized = [serialize_job(job) for job in jobs]

        # ✅ 3. Write to cache (TTL 5 min)
        redis_client.setex(key, 300, json.dumps(serialized))

        return {
            "source": "db",
            "data": serialized
        }

    finally:
        db.close()


# -------------------------
# SERIALIZER (IMPORTANT)
# -------------------------
def serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "source": job.source,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": job.currency,
        "job_type": job.job_type,
        "experience_level": job.experience_level,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }