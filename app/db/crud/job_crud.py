from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, case, desc, text, or_
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
    # 🔹 normalize + tokenize
    tokens = [t.lower().strip() for t in query.split() if t.strip()]

    if not tokens:
        return [], 0

    filters = []
    score_expr = 0

    for token in tokens:
        pattern = f"%{token}%"

        title_match = Job.title.ilike(pattern)
        company_match = Job.company.ilike(pattern)

        # scoring
        score_expr += case((title_match, 3), else_=0)
        score_expr += case((company_match, 2), else_=0)

        filters.append(title_match)
        filters.append(company_match)

    # 🔹 recency boost
    score_expr += case(
        (Job.created_at >= func.now() - text("interval '7 days'"), 1),
        else_=0
    )

    # 🔹 base query
    base_query = db.query(Job, score_expr.label("score")).filter(
        or_(*filters)
    )

    # 🔥 FIX: relaxed location filter
    if location and location.lower() not in ["india", "remote", "any"]:
        base_query = base_query.filter(
            Job.location.ilike(f"%{location}%")
        )

    # 🔹 total count (same filters)
    count_query = db.query(func.count()).select_from(Job).filter(
        or_(*filters)
    )

    if location and location.lower() not in ["india", "remote", "any"]:
        count_query = count_query.filter(
            Job.location.ilike(f"%{location}%")
        )

    total = count_query.scalar()

    # 🔹 results
    results = (
        base_query
        .order_by(desc("score"), Job.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    jobs = [row[0] for row in results]

    return jobs, total