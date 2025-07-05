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
        return
