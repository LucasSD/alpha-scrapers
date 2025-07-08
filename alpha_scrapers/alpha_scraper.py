"""
AlphaScraper module
Provides the AlphaScraper class for scraping job boards with built-in retry logic.
"""
from datetime import datetime
import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from alpha_scrapers.utils.io import save_raw_response

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
        # Generate a run-wide timestamp for raw response saving
        self._run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_raw_response(self, content, filename: str):
        """
        Save a raw response (HTML, JSON, etc.) to the appropriate timestamped directory for this run.

        :param content: The response content to save (HTML, JSON, etc.), as a string or bytes.
        :type content: str or bytes
        :param filename: The filename to use for saving the response (e.g., 'jobs_listing.html').
        :type filename: str
        :returns: None
        :rtype: None
        """
        save_raw_response(content, self.__class__.__name__.replace('Scraper','').lower(), filename, timestamp=self._run_timestamp)

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
