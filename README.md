# alpha-scrapers

Python scrapers for:

1. **Cisco Jobs** (HTML + API + DB + JSON)
2. **(TBC)**

---

## 1. Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:LucasSD/alpha-scrapers.git
   cd alpha-scrapers
   ```

2. **Install dependencies**:
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

- It will fetch the Cisco “SearchJobs” page, extract each job’s detail,
- **Persist** into a local SQLite DB at `data/cisco_jobs.db` (creating the file if needed),
- **Archive** a timestamped JSON under `data/archive/YYYYMMDDTHHMMSSZ.json`,
- **Overwrite** `data/latest.json` with the newest snapshot.

---

## 🔍 Database Persistence

- **File:** `data/cisco_jobs.db`.
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

- **`data/archive/YYYYMMDDTHHMMSSZ.json`** — immutable snapshot per run
- **`data/latest.json`** — overwritten each run, contains the most recent full set
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

---

---
