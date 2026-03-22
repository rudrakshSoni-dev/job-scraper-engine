from app.workers.scrape_tasks import run_scraper

run_scraper.delay("Backend")
