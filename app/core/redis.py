import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_conn = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0")
)