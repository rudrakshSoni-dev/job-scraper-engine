from sqlalchemy.dialects.postgresql import insert
from app.models.job import Job
from sqlalchemy import func


def bulk_upsert_jobs(db, jobs: list[dict]):
    if not jobs:
        return 0

    stmt = insert(Job).values(jobs)

    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "external_id"],  # CRITICAL
        set_={
            "title": stmt.excluded.title,
            "company": stmt.excluded.company,
            "location": stmt.excluded.location,
            "url": stmt.excluded.url,
            "posted_at": stmt.excluded.posted_at,
            "scraped_at": func.now(),
        }
    )

    result = db.execute(stmt)
    db.commit()

    return result.rowcount