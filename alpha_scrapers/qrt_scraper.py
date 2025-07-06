import logging

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        Fetch any URL and return a BeautifulSoup object for parsing.
        """
        response = self.session.get(url, params=params)
        logging.info(f"GET {url} → {response.status_code}")
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def fetch_listings_page(self, params: dict = None) -> BeautifulSoup:
        """
        Fetch and parse the main listings page.
        """
        return self.fetch_page(self.BASE_URL, params)

    def run(self):
        soup = self.fetch_listings_page()
        # breakpoint()


if __name__ == "__main__":
    scraper = QrtScraper()
    data = scraper.run()
