
from sqlalchemy import Column, String, DateTime, UniqueConstraint
from app.db.base import Base

class SearchMetadata(Base):
    __tablename__ = "search_metadata"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    location = Column(String, index=True)
    last_scraped_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("query", "location", name="uq_query_location"),
    )