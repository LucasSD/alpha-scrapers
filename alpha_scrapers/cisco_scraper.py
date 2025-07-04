import requests
from bs4 import BeautifulSoup


class CiscoScraper:
    """
    Basic scraper for the Cisco job search page.
    """

    BASE_URL = "https://jobs.cisco.com/jobs/SearchJobs/"

    def __init__(self):
        self.session = requests.Session()

    def fetch_listings_page(self, params: dict = None) -> BeautifulSoup:
        """
        GET the Cisco SearchJobs page and return a BeautifulSoup object.
        """
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # breakpoint()
        return soup


if __name__ == "__main__":
    scraper = CiscoScraper()
    soup = scraper.fetch_listings_page()
