# app/services/lock.py

def lock_key(query: str, location: str) -> str:
    return f"lock:scrape:{query}:{location}"


def acquire_lock(redis, key: str, ttl=300):
    return redis.set(key, "1", nx=True, ex=ttl)


def release_lock(redis, key: str):
    redis.delete(key)