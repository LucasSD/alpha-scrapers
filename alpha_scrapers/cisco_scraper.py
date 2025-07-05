import logging
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from alpha_scrapers.exporters import dump_to_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class LinkExtractionError(Exception):
    pass


class CiscoScraper:
    """
    Basic scraper for the Cisco job search page.
    """

    BASE_URL = "https://jobs.cisco.com/jobs/SearchJobs/"

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

    def get_job_links(self, soup: BeautifulSoup) -> list[str]:
        """
        Get the job links from the listings page.
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
        Helper to find a <div> with exact text == label,
        then return text of its sibling <div class='fields-data_value'>.
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
        Extract the job title.
        """
        tag = soup.find("h2", class_="title_page-1")
        if tag and tag.get_text(strip=True):
            return tag.get_text(strip=True)
        return ""

    def run(self):
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


if __name__ == "__main__":
    scraper = CiscoScraper()
    data = scraper.run()

    from alpha_scrapers.db import SqlitePersister

    db_path = Path(__file__).parent.parent / "data" / "cisco_jobs.db"
    persister = SqlitePersister(str(db_path))
    persister.save_jobs(data)

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    project_root = Path(__file__).parent.parent

    # Archive folder: data/archive/20250704T153000Z.json
    archive_path = project_root / "data" / "archive" / f"{now}.json"
    # Latest overwrite
    latest_path = project_root / "data" / "latest.json"

    dump_to_json(data, str(archive_path))
    dump_to_json(data, str(latest_path))

    print(f"✅ Wrote {len(data)} records to DB and JSON:")
    print(f"   • SQLite DB: {db_path}")
    print(f"   • Archive:   {archive_path}")
    print(f"   • Latest:    {latest_path}")
