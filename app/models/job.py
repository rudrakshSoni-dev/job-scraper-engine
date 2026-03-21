from sqlalchemy import Column, Integer, Text, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(Text, nullable=False)
    company = Column(Text, nullable=False)
    location = Column(Text)

    description = Column(Text)

    source = Column(String(50), nullable=False)
    url = Column(Text)

    hash = Column(String(64), unique=True, nullable=False, index=True)

    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String(10))

    job_type = Column(String(50))
    experience_level = Column(String(50))

    posted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())