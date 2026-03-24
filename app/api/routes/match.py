# app/api/match.py

from fastapi import APIRouter
from app.services.job_service import get_jobs
from app.services.job_matcher import rank_jobs

router = APIRouter()


@router.post("/match")
def match_jobs(payload: dict):

    skills = payload.get("skills", [])
    keywords = payload.get("keywords", [])
    location = payload.get("location", "india")
    page = payload.get("page", 1)
    limit = payload.get("limit", 20)

    if not skills and not keywords:
        return {"error": "skills or keywords required"}

    # 🔹 build query
    query = " ".join(keywords if keywords else skills)

    # 🔹 fetch jobs (already ranked + paginated)
    result = get_jobs(query, location, page, limit)
    jobs = result["data"]

    # 🔹 match (lightweight scoring layer)
    ranked = rank_jobs(jobs, skills)

    return {
        "meta": result["meta"],
        "results": ranked
    }