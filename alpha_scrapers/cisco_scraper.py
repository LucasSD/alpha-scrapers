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

    def fetch_page(self, url: str, params: dict = None) -> BeautifulSoup:
        """
        Fetch any URL and return a BeautifulSoup object for parsing.
        """
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def fetch_listings_page(self, params: dict = None) -> BeautifulSoup:
        """
        Fetch and parse the main listings page.
        """
        return self.fetch_page(self.BASE_URL, params)

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

    def fetch_job_pages(self, links: list[str]) -> list[BeautifulSoup]:
        """
        Fetch and parse each job URL.
        """
        soup_list = []
        # TODO: remove restriction below
        for url in links[:2]:
            soup = self.fetch_page(url)
            soup_list.append(soup)
        return soup_list

    def run(self):
        soup = self.fetch_listings_page()
        job_links = self.get_job_links(soup)
        job_pages = self.fetch_job_pages(job_links)
        # breakpoint()
        return


if __name__ == "__main__":
    scraper = CiscoScraper()
    scraper.run()
