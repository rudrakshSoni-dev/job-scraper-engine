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
    # 🔹 tokenize query
    tokens = [t.strip() for t in query.split() if t.strip()]

    if not tokens:
        return [], 0

    # 🔹 scoring
    score_expr = 0
    filters = []

    for token in tokens:
        pattern = f"%{token}%"

        title_score = case(
            (Job.title.ilike(pattern), 3),
            else_=0
        )

        company_score = case(
            (Job.company.ilike(pattern), 2),
            else_=0
        )

        score_expr += title_score + company_score

        filters.append(Job.title.ilike(pattern))
        filters.append(Job.company.ilike(pattern))

    # 🔹 recency boost (once)
    recency_score = case(
        (Job.created_at >= func.now() - text("interval '7 days'"), 1),
        else_=0
    )

    score_expr += recency_score

    # 🔹 base query
    base_query = db.query(Job, score_expr.label("score")).filter(
        or_(*filters)
    )

    if location:
        base_query = base_query.filter(
            Job.location.ilike(f"%{location}%")
        )

    # 🔹 count query (same filters, no scoring)
    count_query = db.query(func.count()).select_from(Job).filter(
        or_(*filters)
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