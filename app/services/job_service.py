import json
from app.core.redis_client import redis_client
from app.db.session import SessionLocal
from app.models.job import Job
from app.db.crud.job_crud import get_jobs_paginated


def cache_key(query: str, location: str, page: int, limit: int) -> str:
    return f"jobs:{query}:{location}:{page}:{limit}"


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


def get_jobs(query: str, location: str, page: int = 1, limit: int = 20):
    key = cache_key(query, location, page, limit)

    # CACHE READ
    cached = redis_client.get(key)
    if cached:
        print("CACHE HIT")
        return json.loads(cached)

    print("CACHE MISS")

    db = SessionLocal()
    try:
        offset = (page - 1) * limit

        # use paginated query
        jobs, total = get_jobs_paginated(
            db, query, location, limit, offset
        )

        data = [serialize_job(j) for j in jobs]

        response = {
            "source": "db",
            "data": data,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_more": offset + limit < total
            }
        }

        # cache only if data exists
        if data:
            redis_client.setex(key, 300, json.dumps(response))

        return response

    finally:
        db.close()