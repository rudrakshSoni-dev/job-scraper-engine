from playwright.sync_api import sync_playwright
from app.scraper.base import BaseScraper
from app.scraper.extractors.indeed_extractor import extract_job

import logging
import random
import time
import hashlib

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]


def human_delay(a=2, b=4):
    time.sleep(random.uniform(a, b))


def generate_external_id(job: dict) -> str:
    base = f"{job.get('title')}_{job.get('company')}_{job.get('location')}"
    return hashlib.md5(base.encode()).hexdigest()


class PlaywrightScraper(BaseScraper):

    def scrape_jobs(self) -> list[dict]:
        """
        NEW: No query input
        Uses config-driven scraping
        """
        from app.core.config import SEARCH_TERMS, LOCATION

        all_jobs = []

        for query in SEARCH_TERMS:
            jobs = self._run_scraper(query, LOCATION)
            all_jobs.extend(jobs)

        return all_jobs

    def _run_scraper(self, query: str, location: str) -> list[dict]:

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )

            page = context.new_page()

            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            url = f"https://in.indeed.com/jobs?q={query}&l={location}"
            logger.info(f"[Playwright] {url}")

            jobs = []
            seen_urls = set()

            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)

                if "Just a moment" in page.title():
                    raise Exception("Blocked by Cloudflare")

                page_count = 0
                MAX_PAGES = 3
                DUPLICATE_THRESHOLD = 5
                duplicate_count = 0

                while True:
                    page_count += 1
                    human_delay()

                    cards = page.query_selector_all("div.job_seen_beacon")

                    if not cards:
                        break

                    for card in cards:
                        try:
                            job = extract_job(card)

                            if not job:
                                continue

                            if job["url"] in seen_urls:
                                duplicate_count += 1
                                continue

                            seen_urls.add(job["url"])

                            job["source"] = "indeed"
                            job["query"] = query
                            job["location"] = job.get("location", "").lower()

                            job["external_id"] = generate_external_id(job)

                            jobs.append(job)

                        except Exception as e:
                            logger.warning(f"Extraction error: {e}")

                    logger.info(f"Jobs: {len(jobs)}")

                    # EARLY STOP 
                    if duplicate_count >= DUPLICATE_THRESHOLD:
                        logger.info("Stopping early due to duplicates")
                        break

                    if page_count >= MAX_PAGES:
                        break

                    next_btn = (
                        page.query_selector("a[aria-label='Next']")
                        or page.query_selector("a[data-testid='pagination-page-next']")
                    )

                    if not next_btn:
                        break

                    next_btn.click()
                    page.wait_for_timeout(3000)

                return jobs

            finally:
                context.close()
                browser.close()