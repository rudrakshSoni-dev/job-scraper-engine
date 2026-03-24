from fastapi import FastAPI
from app.api.routes.search import router as search_router
from app.api.routes.match import router as match_router

app = FastAPI()

# include routes
app.include_router(search_router)
app.include_router(match_router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Welcome to the Job Scraper Service!"}