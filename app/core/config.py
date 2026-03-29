# app/core/config.py
SEARCH_TERMS = [
    "backend developer",
    "python developer",
    "software engineer"
]

LOCATION = "india"
FRESHNESS_TTL = 60 * 30  # 30 minutes
LOCK_TTL = 60 * 5        # 5 minutes (for redis lock)