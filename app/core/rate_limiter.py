import time

USER_REQUESTS = {}

FREE_LIMIT = 3  # per day


def check_rate_limit(user_id: str):
    now = time.time()

    if user_id not in USER_REQUESTS:
        USER_REQUESTS[user_id] = []

    # keep only last 24h requests
    USER_REQUESTS[user_id] = [
        t for t in USER_REQUESTS[user_id] if now - t < 86400
    ]

    if len(USER_REQUESTS[user_id]) >= FREE_LIMIT:
        return False

    USER_REQUESTS[user_id].append(now)
    return True