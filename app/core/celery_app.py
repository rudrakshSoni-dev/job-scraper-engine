from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "job_scraper",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="Asia/Kolkata",
    enable_utc=False,

    # fix warning
    broker_connection_retry_on_startup=True,
)

#IMPORTANT: autodiscover FIRST
celery_app.autodiscover_tasks(["app.tasks"])

# FORCE import (fix unregistered task issue)
import app.tasks.scrape_tasks  # keep this AFTER celery_app init

# SCHEDULER
celery_app.conf.beat_schedule = {
    "scrape-jobs-every-3-hours": {
        "task": "app.tasks.scrape_tasks.scrape_jobs_task",
        "schedule": crontab(minute=0, hour="*/3"),
    },
}