from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "job_worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# ✅ ADD THIS LINE
celery.autodiscover_tasks(["app.workers"])