from fastapi import APIRouter, HTTPException

from app.tasks.scrape_tasks import scrape_jobs_task
from app.core.rate_limiter import check_rate_limit
from app.services.job_service import get_jobs
from app.services.freshness import is_fresh
from app.services.lock import lock_key, acquire_lock

from app.db.session import SessionLocal
from app.core.redis_client import redis_client

router = APIRouter()


@router.post("/search")
def search_jobs(payload: dict):
    user_id = payload.get("user_id", "anonymous")

    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    query = payload.get("query")
    location = payload.get("location", "india")

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    #normalize
    query = query.strip().lower()
    location = location.strip().lower()

    #read path (cache + DB)
    result = get_jobs(query, location)

    response = {
        "status": "cached" if result["source"] == "cache" else "db",
        "data": result["data"]
    }

    #freshness check
    db = SessionLocal()
    try:
        fresh = is_fresh(db, query, location)
    finally:
        db.close()

    #scraping decision
    if not fresh:
        key = lock_key(query, location)
        locked = acquire_lock(redis_client, key)

        if locked:
            scrape_jobs_task.delay({
                "query": query,
                "location": location
            })
        # else: already in progress → do nothing
    return response


# DEBUG ONLY
@router.get("/result/{task_id}")
def get_result(task_id: str):
    from celery.result import AsyncResult

    result = AsyncResult(task_id)

    return {
        "state": result.state,
        "result": str(result.result) if result.ready() else None
    }


# READ API
@router.get("/jobs")
def read_jobs(query: str, location: str):
    query = query.strip().lower()
    location = location.strip().lower()

    result = get_jobs(query, location)

    return {
        "status": result["source"],
        "count": len(result["data"]),
        "data": result["data"]
    }