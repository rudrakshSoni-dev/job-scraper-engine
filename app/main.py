from fastapi import FastAPI
from app.models.job import Job
from app.models.search_metadata import SearchMetadata

from app.api.routes.search import router as search_router
from app.api.routes.match import router as match_router
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(search_router)
app.include_router(match_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Welcome to the Job Scraper Service!"}