from celery import Celery

celery_app = Celery(
    "job_scraper",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])

import app.tasks.scrape_tasks