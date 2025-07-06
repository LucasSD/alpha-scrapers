import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class AlphaScraper:
    """
    Base scraper class for job boards, providing a requests session with retry logic.
    """

    def __init__(self):
        self.session = requests.Session()
        # (In production, configure HTTP/S proxies here)
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_listings_page(self, params: Optional[dict] = None) -> Any:
        """
        Fetch and parse the main listings page.
        The return type depends on the implementation of fetch_page in the child class.
        """
        return self.fetch_page(self.BASE_URL, params)
