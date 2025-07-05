import sqlite3


class SqlitePersister:
    """
    Handles SQLite persistence for the jobs table.
    """

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        """
        Create the jobs table if it doesn't exist.
        """
        cur = self.conn.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id     TEXT PRIMARY KEY,
            title      TEXT,
            location   TEXT,
            type       TEXT,
            url        TEXT,
            first_seen TIMESTAMP,
            last_seen  TIMESTAMP
        )
        """
        )
        self.conn.commit()

    def save_jobs(self, records):
        """
        Insert new jobs or update existing ones based on job_id.
        first_seen is set on insert; last_seen always updated.
        """
        cur = self.conn.cursor()
        for rec in records:
            ts = rec.get("scraped_at")
            cur.execute(
                """
            INSERT INTO jobs (job_id, title, location, type, url, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                title = excluded.title,
                location = excluded.location,
                type = excluded.type,
                url = excluded.url,
                last_seen = excluded.last_seen
            """,
                (
                    rec.get("job_id"),
                    rec.get("title"),
                    rec.get("location"),
                    rec.get("type"),
                    rec.get("url"),
                    ts,
                    ts,
                ),
            )
        self.conn.commit()
