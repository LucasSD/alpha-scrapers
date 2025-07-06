"""
cisco_scraper module
Provides the CiscoScraper class for scraping Cisco job listings with built-in retry logic and export capabilities.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from alpha_scrapers.alpha_scraper import AlphaScraper
from alpha_scrapers.exporters import dump_to_json


class LinkExtractionError(Exception):
    """
    Exception raised when no job links can be extracted from the listings page.
    """


class CiscoScraper(AlphaScraper):
    """
    Basic scraper for the Cisco job search page.

    :cvar BASE_URL: Base URL for Cisco job search listings.
    :vartype BASE_URL: str
    """

    BASE_URL = "https://jobs.cisco.com/jobs/SearchJobs/"

    def __init__(self):
        super().__init__()

    def fetch_page(self, url: str, params: dict = None) -> BeautifulSoup:
        """
        Fetch any URL and return a BeautifulSoup object for parsing.

        :param url: The URL to fetch.
        :type url: str
        :param params: Optional query parameters to include in the request.
        :type params: dict or None
        :returns: Parsed HTML content.
        :rtype: BeautifulSoup
        :raises requests.RequestException: If the HTTP request fails after retries.
        """
        response = self.session.get(url, params=params)
        logging.info(f"GET {url} → {response.status_code}")
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_job_links(self, soup: BeautifulSoup) -> list[str]:
        """
        Get the job links from the listings page.

        :param soup: BeautifulSoup of the listings page.
        :type soup: BeautifulSoup
        :returns: List of absolute URLs for individual job details.
        :rtype: list[str]
        :raises LinkExtractionError: If no job links are found.
        """
        links = {
            #  ensure relative URLs are handled
            urljoin(self.BASE_URL, a["href"])
            for a in soup.select("table.table_basic-1 a[href*='/jobs/ProjectDetail/']")
        }
        if not links:
            raise LinkExtractionError(
                "No job links found on listings page – selector may be broken"
            )
        return list(links)

    def parse_field(self, soup: BeautifulSoup, label: str) -> str:
        """
        Find a <div> whose text exactly matches `label`, then return its sibling field value.

        :param soup: BeautifulSoup of the job detail page.
        :type soup: BeautifulSoup
        :param label: The exact text label to search for.
        :type label: str
        :returns: Text of the corresponding data value, or empty string if not found.
        :rtype: str
        """
        try:
            label_div = soup.find(
                lambda tag: isinstance(tag, Tag)
                and tag.name == "div"
                and tag.get_text(strip=True) == label
            )
            if label_div:
                value_div = label_div.find_next_sibling(
                    "div", class_="fields-data_value"
                )
                if value_div:
                    return value_div.get_text(strip=True)
        except Exception:
            pass
        return ""

    def parse_job_title(self, soup: BeautifulSoup) -> str:
        """
        Extract the job title from the detail page.

        :param soup: BeautifulSoup of the job detail page.
        :type soup: BeautifulSoup
        :returns: The job title text, or empty string if not found.
        :rtype: str
        """
        tag = soup.find("h2", class_="title_page-1")
        if tag and tag.get_text(strip=True):
            return tag.get_text(strip=True)
        return ""

    def run(self):
        """
        Execute the scraper: fetch the listings page, extract job URLs, fetch each job,
        parse fields, and collect structured records.

        :returns: A list of job records, each containing:
                  - url: Job detail URL
                  - job_id: Unique job identifier
                  - title: Job title
                  - location: Job location
                  - type: Job type
                  - scraped_at: ISO-formatted UTC timestamp
        :rtype: list[dict]
        """
        soup = self.fetch_listings_page()
        job_links = self.get_job_links(soup)
        results = []
        ts = datetime.now(timezone.utc).isoformat()  # timestamp per job

        for url in job_links:
            try:
                job_soup = self.fetch_page(url)
                job_id = self.parse_field(job_soup, "Job Id")
                if not job_id:
                    # Extract the job ID (final path segment) cleanly, stripping off any query or fragment
                    job_id = PurePosixPath(urlparse(url).path).name
                    logging.warning(
                        f"Falling back to URL-derived job_id {job_id} for {url}"
                    )
                record = {
                    "url": url,
                    "job_id": job_id,
                    "title": self.parse_job_title(job_soup),
                    "location": self.parse_field(job_soup, "Location:")
                    or self.parse_field(job_soup, "Location"),
                    "type": self.parse_field(job_soup, "Job Type"),
                    "scraped_at": ts,
                }

                # optional logging
                missing = [
                    k for k, v in record.items() if v == "" and k != "scraped_at"
                ]
                if missing:
                    logging.warning(
                        f"Missing {missing} for {record['url']} — selectors may need updating"
                    )
                results.append(record)
            except Exception as e:
                logging.error(f"✖ Failed to fetch {url}: {e}")
                continue

        return results


def main():
    """
    Run the CiscoScraper, persist results to SQLite and JSON files, and archive them.

    :raises Exception: If any file I/O or database operation fails.
    """
    scraper = CiscoScraper()
    data = scraper.run()

    from alpha_scrapers.db import SqlitePersister

    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "cisco" / "cisco_jobs.db"
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_dir = project_root / "data" / "cisco" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{now}.json"
    latest_path = project_root / "data" / "cisco" / "latest.json"

    persister = SqlitePersister(str(db_path))
    persister.save_jobs(data)

    dump_to_json(data, str(archive_path))
    dump_to_json(data, str(latest_path))

    logging.info(f"✅ Wrote {len(data)} records to DB and JSON:")
    logging.info(f"   • SQLite DB: {db_path}")
    logging.info(f"   • Archive:   {archive_path}")
    logging.info(f"   • Latest:    {latest_path}")


if __name__ == "__main__":
    main()
