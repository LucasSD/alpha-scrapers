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
        return

    def save_jobs(self, records):
        return
