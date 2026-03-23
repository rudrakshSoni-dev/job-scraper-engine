from fastapi import APIRouter, HTTPException
from app.tasks.scrape_tasks import scrape_jobs_task
from app.core.rate_limiter import check_rate_limit
from app.services.job_service import get_jobs  # ONLY THIS

router = APIRouter()


# 🔹 TRIGGER SCRAPE
@router.post("/search")
def search_jobs(payload: dict):
    user_id = payload.get("user_id", "anonymous")

    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    query = payload.get("query")
    location = payload.get("location", "india")

    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    # ✅ unified service call (cache + DB handled inside)
    result = get_jobs(query, location)

    if result["source"] == "cache":
        return {
            "status": "cached",
            "data": result["data"]
        }

    # ✅ trigger async scrape
    scrape_jobs_task.delay({
        "query": query,
        "location": location
    })

    return {
        "status": "processing"
    }


# 🔹 DEBUG ONLY
@router.get("/result/{task_id}")
def get_result(task_id: str):
    from celery.result import AsyncResult

    result = AsyncResult(task_id)

    return {
        "state": result.state,
        "result": str(result.result) if result.ready() else None
    }


# 🔹 READ API (DB + CACHE via service)
@router.get("/jobs")
def read_jobs(query: str, location: str):
    result = get_jobs(query, location)

    return {
        "status": result["source"],
        "count": len(result["data"]),
        "data": result["data"]
    }