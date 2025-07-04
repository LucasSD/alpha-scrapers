# Alpha Scrapers

Lightweight Python scraper for Cisco job listings with JSON export (latest + archive).

---

## 1. Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:LucasSD/alpha-scrapers.git
   cd alpha-scrapers
   ```

2. **Install dependencies** (using Poetry):
   ```bash
   poetry install
   ```

This creates an isolated virtual environment and installs the following:
- `requests`, `beautifulsoup4` for web scraping
- `pytest` for running tests
- `pre-commit`, `isort`, `flake8`, `black` for code quality checks

---

## 2. Running the Scraper

From the project root, run:
```bash
poetry run python -m alpha_scrapers.cisco_scraper
```

What happens:

1. **Fetch & parse**: Scrape the Cisco SearchJobs page
2. **Extract data**: Pull each job’s `job_id`, `title`, `location`, and `type`
3. **Persist JSON** to `data/`:
   - **Archive**: `data/archive/<TIMESTAMP>.json` (one snapshot per run)
   - **Latest**: `data/latest.json` (always overwritten)

**Why JSON?**
- **Audit trail**: Timestamped archives give you a full history of every scrape
- **Easy ETL**: `latest.json` simplifies downstream pipelines by pointing to one file for fresh data

---

## 3. Running Tests

Execute all tests with:
```bash
poetry run pytest --disable-warnings -q
```

This validates:
- JSON exporter functionality (file creation, overwriting, handling empty data)
- Any scraper parsing logic tests you add later

---
