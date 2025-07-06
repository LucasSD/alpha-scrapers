import logging
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from alpha_scrapers.utils.extraction import jmes_get

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class QrtScraper:
    """
    Scraper for the QRT job search page.
    """

    BASE_URL = (
        "https://boards-api.greenhouse.io/v1/boards/quberesearchandtechnologies/jobs"
    )

    def __init__(self):
        self.session = requests.Session()
        # (In production, configure HTTP/S proxies here)
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            #  tradeoff whether to add 404 and other error statuses here
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_page(self, url: str, params: dict = None) -> BeautifulSoup:
        """
        Fetch any URL and return a JSON response for parsing.
        """
        response = self.session.get(url, params=params)
        logging.info(f"GET {url} → {response.status_code}")
        response.raise_for_status()
        return response.json()

    def fetch_listings_page(self, params: dict = None) -> BeautifulSoup:
        """
        Fetch and parse the main listings page.
        """
        return self.fetch_page(self.BASE_URL, params)

    def parse_job_type(self, job):
        for entry in jmes_get("metadata", job, []):
            if jmes_get("name", entry, "").casefold() == "experience (for job posting)":
                return jmes_get("value", entry, "")
        return ""

    def run(self):
        data = self.fetch_listings_page()
        jobs = data.get("jobs")
        results = []
        ts = datetime.now(timezone.utc).isoformat()  # timestamp per job
        for job in jobs:
            url = jmes_get("absolute_url", job, "")
            if not (job_id := jmes_get("id", job)):
                # Extract the job ID (final path segment) cleanly, stripping off any query or fragment
                job_id = PurePosixPath(urlparse(url).path).name
                logging.warning(
                    f"Falling back to URL-derived job_id {job_id} for {url}"
                )

            record = {
                "url": url,
                "job_id": job_id,
                "title": jmes_get("title", job, ""),
                "location": jmes_get("location.name", job, ""),
                "type": self.parse_job_type(job),
                "scraped_at": ts,
            }

            # optional logging
            missing = [k for k, v in record.items() if v == "" and k != "scraped_at"]
            if missing:
                logging.warning(
                    f"Missing {missing} for {record['url']} — jmes_paths may need updating"
                )
            results.append(record)

        return results


if __name__ == "__main__":
    scraper = QrtScraper()
    data = scraper.run()
    # breakpoint()
