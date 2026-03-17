#makes a python folder a package, so we can import from it
from app.db.session import SessionLocal, engine #DB Connection and session
# Base is the declarative base class that our models will inherit from
# It is used to define the structure of our database tables and to create the tables in the database.
from app.db.base import Base

__all__ = ["SessionLocal", "engine", "Base", "init_db"]