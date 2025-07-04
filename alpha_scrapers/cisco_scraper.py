from urllib.parse import urljoin

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
        return soup

    def get_job_links(self, soup: BeautifulSoup) -> list[str]:
        """
        Get the job links from the listings page.
        """
        links = {
            urljoin(self.BASE_URL, a["href"])
            for a in soup.select("table.table_basic-1 a[href*='/jobs/ProjectDetail/']")
        }
        # breakpoint()
        return list(links)

    def run(self):
        soup = self.fetch_listings_page()
        job_links = self.get_job_links(soup)
        return job_links


if __name__ == "__main__":
    scraper = CiscoScraper()
    scraper.run()
