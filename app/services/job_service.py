import hashlib
from sqlalchemy.dialects.postgresql import insert
from app.models.job import Job


def generate_hash(job):
    key = f"{job['title'].strip().lower()}-{job['company'].strip().lower()}-{job.get('location','').strip().lower()}"
    return hashlib.sha256(key.encode()).hexdigest()


def bulk_create_jobs(db, jobs: list[dict]):
    valid_jobs = []

    for job in jobs:
        # ✅ protect DB (skip bad data)
        if not job.get("title") or not job.get("company"):
            continue

        job["hash"] = generate_hash(job)
        valid_jobs.append(job)

    if not valid_jobs:
        print("NO VALID JOBS")
        return

    stmt = insert(Job).values(valid_jobs)
    stmt = stmt.on_conflict_do_nothing(index_elements=["hash"])

    db.execute(stmt)
    db.commit()