from sqlalchemy.dialects.postgresql import insert
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