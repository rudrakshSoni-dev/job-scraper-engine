import logging

logger = logging.getLogger(__name__)


def extract_job(card):
    def safe_text(el):
        try:
            return el.inner_text().strip()
        except:
            return None

    try:
        title_el = (
            card.query_selector("h2 a span[title]") or
            card.query_selector("h2 a span") or
            card.query_selector("h2 span")
        )

        company_el = (
            card.query_selector(".companyName") or
            card.query_selector("[data-testid='company-name']")
        )

        location_el = (
            card.query_selector(".companyLocation") or
            card.query_selector("[data-testid='job-location']") or
            card.query_selector("[data-testid='text-location']")
        )

        link_el = card.query_selector("h2 a")

        job_url = None
        if link_el:
            href = link_el.get_attribute("href")
            if href:
                if href.startswith("http"):
                    job_url = href
                else:
                    job_url = "https://in.indeed.com" + href

        title = safe_text(title_el)
        company = safe_text(company_el)

        location = safe_text(location_el)
        if location:
            location = location.replace("\n", " ").strip()

        if not title or not company:
            logger.warning(f"Invalid job skipped: title={title}, company={company}")
            return None

        job = {
            "title": title,
            "company": company,
            "location": location,
            "url": job_url
        }

        return job

    except Exception as e:
        logger.warning(f"Extractor error: {e}")
        return None