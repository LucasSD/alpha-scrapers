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

 - **Python 3.10 or greater**
   We recommend using [pyenv](https://github.com/pyenv/pyenv) to install and manage your Python versions.
   ```bash
   pyenv install 3.xx.x
   pyenv local 3.xx.x
   ```

 - **Poetry** for dependency & environment management
   Official guide if needed: [Poetry Documentation](https://python-poetry.org/docs/)

---

## 1. Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:LucasSD/alpha-scrapers.git
   cd alpha-scrapers
   ```
2. ```bash
   pyenv local 3.xx.x
   poetry env use "$(pyenv which python)"
   ```

   If you don’t use pyenv, just be sure your python --version is ≥3.10 and that Poetry picks it up. For example, you can explicitly point Poetry at your interpreter:
   ```bash
   # if python3.10 is on your PATH
   poetry env use python3.10
   ```

3. **Install dependencies**:
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
poetry run python -m alpha_scrapers.qrt_scraper
```

- They will extract each job’s detail,
- **Persist** into a local SQLite DB at `data/<target_name>/<target_name>_jobs.db` (creating the file if needed),
- **Archive** a timestamped JSON under `data/<target_name>/archive/YYYYMMDDTHHMMSSZ.json`,
- **Overwrite** `data/<target_name>/latest.json` with the newest snapshot.

---

## 🔍 Database Persistence
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

## 📁 JSON Output

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

## 3. Running Tests

Execute all tests with:
```bash
poetry run pytest
```

## 📝 Style & Pre-commit Hooks

We use:

- **Black** (⎋ formatting)
- **isort** (import sorting)
- **flake8** (linting)
- **pre-commit** to enforce them on every commit

Run **all** hooks locally:

```bash
poetry run pre-commit run --all-files
```

## Improvements

 - Switch to async (using `aiohttp` or `httpx`) for higher throughput when scraping many pages.
 - find further DRY improvements
 - use walrus operator more consistently

---

---
