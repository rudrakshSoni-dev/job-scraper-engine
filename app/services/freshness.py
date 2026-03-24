# app/services/freshness.py

from datetime import datetime, timedelta
from app.core.config import FRESHNESS_TTL
from app.models.search_metadata import SearchMetadata

def is_fresh(db, query: str, location: str) -> bool:
    record = (
        db.query(SearchMetadata)
        .filter_by(query=query, location=location)
        .first()
    )

    if not record or not record.last_scraped_at:
        return False

    return datetime.utcnow() - record.last_scraped_at < timedelta(seconds=FRESHNESS_TTL)