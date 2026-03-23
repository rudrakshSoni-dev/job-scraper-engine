from playwright.sync_api import sync_playwright
from app.scraper.extractors.indeed_extractor import extract_job
import logging
import random
import time

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]


def human_delay(a=2, b=5):
    time.sleep(random.uniform(a, b))


class PlaywrightScraper:

    def scrape_jobs(self, query: str, location: str):
        for attempt in range(3):
            try:
                logger.info(f"Attempt {attempt + 1}")

                jobs = self._run_scraper(query, location)

                if jobs:   # ✅ success condition
                    return jobs

                raise Exception("No jobs scraped")

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(random.uniform(5, 10))

        raise Exception("Scraping failed after retries")

    def _run_scraper(self, query: str, location: str):

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=False,
                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                slow_mo=100
            )

            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )

            page = context.new_page()

            # stealth
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            url = f"https://in.indeed.com/jobs?q={query}&l={location}"
            logger.info(f"Opening URL: {url}")

            try:
                page.goto(url, timeout=60000)

                # ✅ ONLY WAIT (NO selector waits anywhere)
                page.wait_for_timeout(5000)

                logger.info(f"Page title: {page.title()}")

                if "Just a moment" in page.title():
                    raise Exception("Blocked by Cloudflare")

                active_selector = "div.job_seen_beacon"

                jobs = []
                seen_urls = set()

                page_count = 0
                MAX_PAGES = 3

                while True:
                    page_count += 1
                    logger.info(f"Scraping page {page_count}")

                    if page.is_closed():
                        break

                    human_delay(2, 4)

                    cards = page.query_selector_all(active_selector)
                    logger.info(f"Cards found: {len(cards)}")

                    if not cards:
                        logger.warning("No cards → retry once")
                        page.wait_for_timeout(4000)
                        cards = page.query_selector_all(active_selector)

                        if not cards:
                            break

                    # debug (safe)
                    try:
                        logger.info(cards[0].inner_text()[:200])
                    except:
                        pass

                    for card in cards:
                        try:
                            job = extract_job(card)

                            if job and job.get("url") not in seen_urls:
                                seen_urls.add(job.get("url"))
                                jobs.append(job)

                        except Exception as e:
                            logger.warning(f"Extraction error: {e}")

                    logger.info(f"Total jobs collected: {len(jobs)}")

                    if page_count >= MAX_PAGES:
                        break

                    next_btn = (
                        page.query_selector("a[aria-label='Next']") or
                        page.query_selector("a[data-testid='pagination-page-next']")
                    )

                    if not next_btn:
                        logger.info("No next button → ending")
                        break

                    try:
                        next_btn.click()
                        page.wait_for_timeout(4000)
                    except Exception as e:
                        logger.warning(f"Pagination failed: {e}")
                        break

                logger.info(f"Sample jobs: {jobs[:2]}")

                return jobs   # ✅ ALWAYS return, never fail here

            finally:
                context.close()
                browser.close()

# KEPT FOR LATER - SCALABLE VERSION 
# from playwright.sync_api import sync_playwright
# from scraper.extractors.indeed_extractor import extract_job
# from scraper.proxy.proxy_manager import ProxyManager
# import logging
# import random
# import time

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#     "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# ]

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# proxy ={
#     "server":"http://host:port",
#     "username":"user",
#     "password":"pass"
# }

# def human_delay(a=1, b=3):
#     time.sleep(random.uniform(a, b))


# class PlaywrightScraper:
#     def __init__(self):
#         self.playwright = None
#         self.context = None
#         self.proxy_manager = ProxyManager()

#     # ---------------------------
#     # START / STOP
#     # ---------------------------
#     def start(self):
#         self.playwright = sync_playwright().start()

#         proxy = self.proxy_manager.get_proxy()
#         logger.info(f"Using proxy: {proxy['server']}")

#         self.context = self.playwright.chromium.launch_persistent_context(
#             user_data_dir="./playwright_data",
#             headless=False,
#             executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#             proxy=proxy,
#             slow_mo=200,
#             args=[
#                 "--start-maximized",
#                 "--disable-blink-features=AutomationControlled",
#             ]
#         )

#         page = self.context.new_page()
#         page.goto("https://www.indeed.com", timeout=60000)

#         logger.info("Browser started")

#     def stop(self):
#         logger.info("Stopping browser")

#         if self.context:
#             self.context.close()

#         if self.playwright:
#             self.playwright.stop()

#     # ---------------------------
#     # PUBLIC METHOD (WITH RETRY)
#     # ---------------------------
#     def scrape_jobs(self, query: str, location: str):
#         for attempt in range(3):
#             try:
#                 logger.info(f"Attempt {attempt+1}")
#                 return self._scrape_jobs(query, location)

#             except Exception as e:
#                 logger.error(f"Attempt {attempt+1} failed: {e}")

#                 # restart context with new proxy
#                 self._restart_with_new_proxy()

#                 human_delay(2, 5)

#         raise Exception("Failed after 3 attempts")

#     # ---------------------------
#     # INTERNAL SCRAPER
#     # ---------------------------
#     def _scrape_jobs(self, query: str, location: str):
#         page = self.context.new_page()

#         page.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             });
#         """)

#         url = f"https://www.indeed.com/jobs?q={query}&l={location}"

#         page.goto(url, timeout=60000)

#         logger.info(f"URL: {page.url}")
#         logger.info(f"Title: {page.title()}")

#         # block detection
#         if "Just a moment" in page.title():
#             raise Exception("Blocked")

#         page.wait_for_selector("a.tapItem", timeout=15000)

#         jobs = []
#         page_count = 0
#         MAX_PAGES = 10

#         while True:
#             page_count += 1
#             logger.info(f"Page {page_count}")

#             page.mouse.wheel(0, random.randint(1000, 2000))
#             human_delay(1, 2)

#             cards = page.query_selector_all("a.tapItem")

#             if len(cards) == 0:
#                 logger.warning("Empty page → reload")

#                 page.reload()
#                 page.wait_for_selector("a.tapItem", timeout=15000)

#                 cards = page.query_selector_all("a.tapItem")

#                 if len(cards) == 0:
#                     break

#             for card in cards:
#                 job = extract_job(card)

#                 if job["title"] and job["company"]:
#                     jobs.append(job)

#             logger.info(f"Jobs collected: {len(jobs)}")

#             if page_count >= MAX_PAGES:
#                 break

#             next_btn = page.query_selector("a[aria-label='Next']")

#             if not next_btn or not next_btn.is_enabled():
#                 break

#             next_btn.click()
#             page.wait_for_selector("a.tapItem", timeout=15000)

#         page.close()
#         return jobs

#     # ---------------------------
#     # PROXY RESTART
#     # ---------------------------
#     def _restart_with_new_proxy(self):
#         logger.info("Restarting with new proxy")

#         if self.context:
#             self.context.close()

#         proxy = self.proxy_manager.get_proxy()
#         logger.info(f"New proxy: {proxy['server']}")

#         self.context = self.playwright.chromium.launch_persistent_context(
#             user_data_dir="./playwright_data",
#             headless=False,
#             executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#             proxy=proxy,
#         )