"""
sqlite_persister module
Handles persistence of job records into an SQLite database.
"""

import sqlite3
from pathlib import Path


class SqlitePersister:
    """
    Handles SQLite persistence for the jobs table.

    :ivar conn: Active SQLite connection.
    :vartype conn: sqlite3.Connection
    """

    def __init__(self, db_path: str):
        """
        Initialize the persister by ensuring the database directory exists,
        connecting to the SQLite database, and creating the schema if needed.

        :param db_path: Filesystem path to the SQLite database file.
        :type db_path: str
        :raises OSError: If the database directory cannot be created.
        """
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)  # create any missing folders
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        """
        Create the jobs table if it doesn't already exist.

        :returns: None
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
        Sets first_seen on insert; always updates last_seen.

        :param records: List of job record dictionaries containing keys:
                        'job_id', 'title', 'location', 'type', 'url', 'scraped_at'.
        :type records: list[dict]
        :returns: None
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
