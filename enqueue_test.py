from app.workers.tasks import process_job

job_data = {
    "title": "Backend Engineer",
    "company": "Google",
    "location": "Remote",
    "source": "test",
    "url": "test.com"
}

result = process_job.delay(job_data)
print("TASK ID:", result.id)