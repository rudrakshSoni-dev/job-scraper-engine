import json
from app.core.redis_client import redis_client
from app.db.session import SessionLocal
from app.models.job import Job
from sqlalchemy import desc, text, or_


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
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
    }


def get_jobs(query: str, location: str, page: int = 1, limit: int = 20):
    key = cache_key(query, location, page, limit)

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached.decode("utf-8"))

    db = SessionLocal()

    try:
        offset = (page - 1) * limit

        q = db.query(Job)

        if query:
            q = q.filter(Job.title.ilike(f"%{query}%"))

        if location and location not in ["india", "remote", "any"]:
            q = q.filter(Job.location.ilike(f"%{location}%"))

        q = q.filter(
            or_(
                Job.posted_at == None,
                Job.posted_at >= text("NOW() - INTERVAL '7 days'")
            )
        )

        total = q.count()

        jobs = (
            q.order_by(desc(Job.posted_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        data = [serialize_job(j) for j in jobs]

        response = {
            "data": data,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_more": offset + limit < total
            }
        }

        if data:
            redis_client.setex(key, 300, json.dumps(response))

        return response

    finally:
        db.close()