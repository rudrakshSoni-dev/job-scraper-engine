from app.workers.queue import queue

job_data = {
    "title": "Backend Engineer",
    "company": "Google",
    "location": "Remote",
    "source": "test",
    "url": "test.com"
}

queue.enqueue("app.workers.tasks.process_job", job_data)