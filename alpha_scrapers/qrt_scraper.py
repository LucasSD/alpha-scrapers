import logging
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from alpha_scrapers.alpha_scraper import AlphaScraper
from alpha_scrapers.exporters import dump_to_json
from alpha_scrapers.utils.extraction import jmes_get

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class QrtScraper(AlphaScraper):
    """
    Scraper for the QRT job search page.
    """

    BASE_URL = (
        "https://boards-api.greenhouse.io/v1/boards/quberesearchandtechnologies/jobs"
    )

    def __init__(self):
        super().__init__()

    def fetch_page(self, url: str, params: dict = None) -> dict:
        """
        Fetch any URL and return a JSON response for parsing.
        """
        response = self.session.get(url, params=params)
        logging.info(f"GET {url} → {response.status_code}")
        response.raise_for_status()
        return response.json()

    def fetch_listings_page(self, params: dict = None) -> dict:
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
        jobs = jmes_get("jobs", data, [])
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


def main():
    scraper = QrtScraper()
    data = scraper.run()

    from alpha_scrapers.db import SqlitePersister

    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "qrt" / "qrt_jobs.db"
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_dir = project_root / "data" / "qrt" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{now}.json"
    latest_path = project_root / "data" / "qrt" / "latest.json"

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
