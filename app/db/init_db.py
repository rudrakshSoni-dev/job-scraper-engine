from app.db.session import engine
from app.db.base import Base

# 🔴 IMPORTANT: import models here
from app.models.job import Job


def init_db():
    Base.metadata.create_all(bind=engine)