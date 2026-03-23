from fastapi import FastAPI
from app.api.routes.search import router as search_router

app = FastAPI()

# include routes
app.include_router(search_router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Welcome to the Job Scraper Service!"}