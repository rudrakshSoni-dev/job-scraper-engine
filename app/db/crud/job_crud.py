from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, case, desc, text
from app.models.job import Job


def bulk_insert_jobs(db, jobs: list[dict]):
    if not jobs:
        return 0

    stmt = insert(Job).values(jobs)

    stmt = stmt.on_conflict_do_nothing(
        index_elements=["hash"]
    )

    result = db.execute(stmt)
    db.commit()

    return result.rowcount


def get_jobs_paginated(db, query, location, limit=20, offset=0):
    query_pattern = f"%{query}%"

    # 🔹 scoring logic
    title_score = case(
        (Job.title.ilike(query_pattern), 3),
        else_=0
    )

    company_score = case(
        (Job.company.ilike(query_pattern), 2),
        else_=0
    )

    # ✅ correct recency (Postgres interval)
    recency_score = case(
        (Job.created_at >= func.now() - text("interval '7 days'"), 1),
        else_=0
    )

    total_score = title_score + company_score + recency_score

    # 🔹 base query (with score)
    base_query = db.query(Job, total_score.label("score")).filter(
        Job.title.ilike(query_pattern) |
        Job.company.ilike(query_pattern)
    )

    if location:
        base_query = base_query.filter(
            Job.location.ilike(f"%{location}%")
        )

    # ✅ separate count query (better)
    count_query = db.query(func.count()).select_from(Job).filter(
        Job.title.ilike(query_pattern) |
        Job.company.ilike(query_pattern)
    )

    if location:
        count_query = count_query.filter(
            Job.location.ilike(f"%{location}%")
        )

    total = count_query.scalar()

    # 🔹 ranked results
    results = (
        base_query
        .order_by(desc("score"), Job.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    jobs = [row[0] for row in results]

    return jobs, total