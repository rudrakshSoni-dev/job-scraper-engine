from playwright.sync_api import sync_playwright
from scraper.extractors.indeed_extractor import extract_job
import logging
import random
import time


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))


class PlaywrightScraper:
    def __init__(self):
        self.playwright = None
        self.context = None   # ✅ persistent context

    # ---------------------------
    # START / STOP
    # ---------------------------
    def start(self):
        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir="./playwright_data",
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", 
            slow_mo=200,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        print("Context created")
        print(self.context)

        page = self.context.new_page()
        page.goto("https://www.indeed.com", timeout=60000)

        logger.info("Playwright persistent browser started")

    def stop(self):
        logger.info("Stopping Playwright browser")

        if self.context:
            self.context.close()

        if self.playwright:
            self.playwright.stop()

    # ---------------------------
    # MAIN SCRAPER
    # ---------------------------

    logger.info("Entered scrape_jobs()")
    def scrape_jobs(self, query: str, location: str):
        page = self.context.new_page()

        # stealth patch
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        url = f"https://www.indeed.com/jobs?q={query}&l={location}"

        human_delay(1, 3)
        page.goto(url, timeout=60000)

        # DEBUG (keep for now)
        logger.info(f"URL: {page.url}")
        logger.info(f"Title: {page.title()}")
        page.screenshot(path="initial_load.png")

        # block detection
        if "Just a moment" in page.title():
            logger.error("Blocked by Cloudflare")
            raise Exception("Blocked - solve manually once")

        # wait for job cards (UPDATED SELECTOR)
        page.wait_for_selector("a.tapItem", timeout=15000)
        human_delay(1, 2)

        jobs = []
        page_count = 0
        MAX_PAGES = 10

        while True:
            page_count += 1
            logger.info(f"Scraping page {page_count}")

            # scroll
            page.mouse.wheel(0, random.randint(1000, 2000))
            human_delay(1, 2)

            cards = page.query_selector_all("a.tapItem")
            logger.info(f"Found {len(cards)} job cards")

            # retry logic
            if len(cards) == 0:
                logger.warning("Empty page, retrying...")

                page.reload()
                page.wait_for_selector("a.tapItem", timeout=15000)
                human_delay(1, 2)

                cards = page.query_selector_all("a.tapItem")

                if len(cards) == 0:
                    logger.error("Still empty after retry, skipping page")
                    continue

            for card in cards:
                job = extract_job(card)

                if job["title"] and job["company"]:
                    jobs.append(job)

            logger.info(f"Total jobs so far: {len(jobs)}")

            # stop condition
            if page_count >= MAX_PAGES:
                logger.info("Reached max pages limit")
                break

            # pagination
            next_btn = page.query_selector("a[aria-label='Next']")

            if not next_btn or not next_btn.is_enabled():
                logger.info("No next button, pagination ended")
                break

            logger.info("Going to next page")

            next_btn.click()

            page.wait_for_selector("a.tapItem", timeout=15000)
            human_delay(1, 2)

        page.close()
        return 
        