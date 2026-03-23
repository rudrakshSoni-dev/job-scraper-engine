from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.tasks.scrape_tasks import scrape_jobs_task
from app.core.rate_limiter import check_rate_limit

router = APIRouter()


@router.post("/search")
def search_jobs(payload: dict):
    user_id = payload.get("user_id", "anonymous")

    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    task = scrape_jobs_task.delay(payload)

    return {
        "task_id": task.id,
        "status": "processing"
    }


@router.get("/result/{task_id}")
def get_result(task_id: str):
    result = AsyncResult(task_id)

    if result.state == "PENDING":
        return {"status": "pending"}

    if result.state == "FAILURE":
        return {"status": "failed"}

    return {
        "status": "completed",
        "data": result.result
    }