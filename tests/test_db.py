# tests/test_db.py

import sqlite3

import pytest

from alpha_scrapers.db import SqlitePersister


def test_jobs_table_created_in_memory():
    """
    Instantiating against ":memory:" should create the 'jobs' table.
    """
    persister = SqlitePersister(":memory:")
    cursor = persister.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';")
    assert cursor.fetchone() == ("jobs",)


def test_jobs_table_columns_and_pk_in_memory():
    """
    The 'jobs' table in an in-memory DB must have the expected columns and PK.
    """
    persister = SqlitePersister(":memory:")
    cursor = persister.conn.cursor()
    cursor.execute("PRAGMA table_info('jobs');")
    cols = cursor.fetchall()
    col_names = [col[1] for col in cols]
    assert col_names == [
        "job_id",
        "title",
        "location",
        "type",
        "url",
        "first_seen",
        "last_seen",
    ]
    # Verify 'job_id' is primary key (pk flag == 1)
    pk_col = next(col for col in cols if col[1] == "job_id")
    assert pk_col[5] == 1


def test_jobs_table_columns_and_pk_file(tmp_path):
    """
    The 'jobs' table in a file-based DB must have the expected columns and PK,
    and the file should be created.
    """
    db_file = tmp_path / "test.db"
    path = str(db_file)

    persister = SqlitePersister(path)
    # File should exist after initialization
    assert db_file.exists()

    cursor = persister.conn.cursor()
    cursor.execute("PRAGMA table_info('jobs');")
    cols = cursor.fetchall()
    col_names = [col[1] for col in cols]
    assert col_names == [
        "job_id",
        "title",
        "location",
        "type",
        "url",
        "first_seen",
        "last_seen",
    ]
    # Verify 'job_id' is primary key
    pk_col = next(col for col in cols if col[1] == "job_id")
    assert pk_col[5] == 1
