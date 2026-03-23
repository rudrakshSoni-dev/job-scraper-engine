def extract_job(card):
    def safe_text(el):
        return el.inner_text().strip() if el else None

    title = card.query_selector("h2 span")
    company = card.query_selector(".companyName")
    location = card.query_selector(".companyLocation")

    return {
        "title": safe_text(title),
        "company": safe_text(company),
        "location": safe_text(location),
    }