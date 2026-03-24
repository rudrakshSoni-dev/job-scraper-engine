import redis
import os
from dotenv import load_dotenv

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

load_dotenv()

redis_conn = redis.Redis.from_url(
    REDIS_URL
)