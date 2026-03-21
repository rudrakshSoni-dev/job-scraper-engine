from rq import Queue
from app.core.redis import redis_conn

queue = Queue("jobs", connection=redis_conn)