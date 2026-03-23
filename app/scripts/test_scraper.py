from scraper.playwright_scraper import PlaywrightScraper

if __name__ == "__main__":
    scraper = PlaywrightScraper()

    jobs = scraper.scrape_jobs("backend developer", "remote")

    print(f"\nTotal jobs scraped: {len(jobs)}\n")

    for job in jobs[:5]:
        print(job)



# # this is to test without celery worker running, just to see if the task runs without error
# print("Testing scraper running")
# from scraper.playwright_scraper import PlaywrightScraper

# if __name__ == "__main__":
#     scraper = PlaywrightScraper()

#     try:
#         scraper.start()

#         jobs = scraper.scrape_jobs("backend developer", "remote")

#         print(f"\nTotal jobs scraped: {len(jobs)}\n")

#         for j in jobs[:5]:
#             print(j)

#     finally:
#         scraper.stop()