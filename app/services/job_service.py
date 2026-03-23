import json
from sqlalchemy import func
from app.core.redis_client import redis_client
from app.db.session import SessionLocal
from app.models.job import Job


def cache_key(query: str, location: str) -> str:
    return f"jobs:{query}:{location}"


def serialize_job(job: Job):
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "source": job.source,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


def get_jobs(query: str, location: str):
    key = cache_key(query, location)

    # CACHE READ
    cached = redis_client.get(key)
    if cached:
        print("CACHE HIT")
        return {
            "source": "cache",
            "data": json.loads(cached)
        }

    print("CACHE MISS")

    db = SessionLocal()
    try:
        # ✅ MUST BE INSIDE FUNCTION
        jobs = db.query(Job).filter(
            func.trim(Job.query).ilike(f"%{query.strip().lower()}%")
        ).order_by(Job.created_at.desc()).limit(50).all()

        data = [serialize_job(j) for j in jobs]

        if data:
            redis_client.setex(key, 300, json.dumps(data))

        return {
            "source": "db",
            "data": data
        }

    finally:
        db.close()