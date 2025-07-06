"""
AlphaScraper module
Provides the AlphaScraper class for scraping job boards with built-in retry logic.
"""

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
    Base scraper class, providing a requests session with retry logic.

    :ivar session: A configured requests.Session with retry-enabled HTTPAdapter.
    :vartype session: requests.Session
    """

    def __init__(self):
        """
        Initialize the AlphaScraper.

        Sets up a `requests.Session` with retry logic for common transient HTTP errors.

        :raises Exception: If session setup fails.
        """
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

        Delegates to `fetch_page` implemented by subclasses. The return
        type depends on that implementation.

        :param params: Query parameters to include in the request.
        :type params: dict or None
        :returns: Parsed page data, as defined by subclass.
        :rtype: Any
        :raises requests.RequestException: If the HTTP request fails after retries.
        """
        return self.fetch_page(self.BASE_URL, params)
