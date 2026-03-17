from app.db.base import Base
from app.db.session import engine

# IMPORTANT: import models here later
# from app.models.job import Job too


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


if __name__ == "__main__":
    init_db()