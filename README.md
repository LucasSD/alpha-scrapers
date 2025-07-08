# alpha-scrapers

Python scrapers for:

1. **Cisco Jobs** (HTML → DB & JSON)
   - Demonstrates HTML web scraping:
     1. Fetch the main listings page (HTML).
     2. Extract each job’s link.
     3. Request each job’s detail page and parse out the fields.
   - Although the listing page exposes most fields, we scrape each job's page for greater reliability. I avoided making the scraper asyncronous because this was a demonstration of using Python `requests`

2. **QRT Jobs** (JSON → DB & JSON)
   - Shows the alternative of consuming a RESTful API:
     1. Fetch one single JSON payload with *all* jobs.
     2. Extract every field directly (no per-job page requests).
   - Highlights how an API-first approach can be cleaner, faster, and more reliable in production.

---

> **Note:** In a real production context you might choose one approach over the other (HTML vs. API, one listings page vs individual job pages) based on latency, data guarantees, or authorisation, but here both patterns are on display.

---

 **Prerequisites**

 - **Suggested Python version: 3.12.2**
   We recommend using [pyenv](https://github.com/pyenv/pyenv) to install and manage your Python versions.
   ```bash
   pyenv install 3.12.2
   pyenv local 3.12.2
   ```

---

## 1. Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:LucasSD/alpha-scrapers.git
   cd alpha-scrapers
   ```
2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

This creates an isolated virtual environment and installs the following:
- `requests`, `beautifulsoup4`, and `jmespath` for web scraping
- `pytest` for running tests (and `freezegun`)
- `pre-commit` and `ruff` for code quality checks

---

## 2. Running the Scrapers

From the project root, run:
```bash
python -m alpha_scrapers.cisco_scraper
python -m alpha_scrapers.qrt_scraper
```

- They will extract each job’s detail,
- **Persist** into a local SQLite DB at `data/<target_name>/<target_name>_jobs.db` (creating the file if needed),
- **Archive** a timestamped JSON under `data/<target_name>/archive/YYYYMMDDTHHMMSSZ.json`,
- **Overwrite** `data/<target_name>/latest.json` with the newest snapshot.

After running the scrapers, you will also see a `raw_responses/` directory. This contains timestamped archives of the raw HTML and JSON responses fetched by the scrapers, organized by run and by scraper. These files are useful for debugging and auditing what was fetched from the source sites.

---

## 3. Database Persistence
- **Table:** `jobs`, automatically created on first run.
- **Upsert logic:**
  - If a record’s `job_id` is **new**, it’s **inserted** and its `first_seen` and `last_seen` are set to the current timestamp.
  - If `job_id` **already exists**, its `last_seen` is **updated** (and any changed fields like `title`, `location`, `type` are written), but `first_seen` remains the original timestamp when we first saw it.

This design ensures you can:
- **Quickly backfill** all jobs ever seen,
- **Query the delta** since your last run via `last_seen`,
- **Archive JSON** for a point-in-time dump, and
- **Maintain a “latest” JSON** for easy downstream consumption.

---

## 4. JSON Output

- **`archive/YYYYMMDDTHHMMSSZ.json`** — immutable snapshot per run
- **`latest.json`** — overwritten each run, contains the most recent full set
- **Schema per record:**
  ```json
  {
    "url":      "...ProjectDetail/.../1234567",
    "job_id":   "1234567",
    "title":    "Software Engineer",
    "location": "San Jose, California, US",
    "type":     "Professional",
    "scraped_at":"2025-07-06T12:00:00+00:00"
  }
  ```

---

## 5. Running Tests

Execute all tests with:
```bash
pytest
```

## 6. Style & Pre-commit Hooks

We use:

- **ruff** (formatting)
- **pre-commit** to enforce them on every commit

Run **all** hooks locally:

```bash
pre-commit run --all-files
```

## 7. Exploring the SQLite Database

You can inspect and query the job data stored in the SQLite database using either the command line or a graphical tool:

1. **Using the sqlite3 command line tool:**
   ```bash
   sqlite3 data/cisco/cisco_jobs.db
   sqlite> .tables
   sqlite> SELECT * FROM jobs LIMIT 5;
   ```
   (Replace the path with your desired database, e.g., `data/qrt/qrt_jobs.db`)

2. **Using a modern GUI:**
   - We recommend [DB Browser for SQLite](https://sqlitebrowser.org/)

## 8. Improvements

 - Switch to async (using `aiohttp` or `httpx`) for higher throughput when scraping many pages.
 - find further DRY improvements
 - use walrus operator more consistently

---

---
