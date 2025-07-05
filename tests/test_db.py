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


def test_insert_and_update_behavior(tmp_path):
    # 1) Create an in‐memory persister
    persister = SqlitePersister(":memory:")
    now1 = "2025-07-05T12:00:00Z"
    now2 = "2025-07-05T12:05:00Z"

    # Define two records for the same job_id but different scraped_at
    rec1 = {
        "job_id": "J1",
        "title": "Engineer A",
        "location": "London",
        "type": "Professional",
        "url": "https://jobs.cisco.com/J1",
        "scraped_at": now1,
    }
    rec2 = {
        "job_id": "J1",
        "title": "Engineer A (updated)",
        "location": "London, UK",
        "type": "Professional",
        "url": "https://jobs.cisco.com/J1",
        "scraped_at": now2,
    }

    # 2) Save first record
    persister.save_jobs([rec1])
    cursor = persister.conn.cursor()
    cursor.execute(
        "SELECT first_seen, last_seen, title, location FROM jobs WHERE job_id = 'J1'"
    )
    fs, ls, title1, loc1 = cursor.fetchone()
    assert fs == now1
    assert ls == now1
    assert title1 == "Engineer A"
    assert loc1 == "London"

    # 3) Save second record (should trigger update, not insert)
    persister.save_jobs([rec2])
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_id = 'J1'")
    assert cursor.fetchone()[0] == 1

    # Verify first_seen unchanged, last_seen updated, and fields updated
    cursor.execute(
        "SELECT first_seen, last_seen, title, location FROM jobs WHERE job_id = 'J1'"
    )
    fs2, ls2, title2, loc2 = cursor.fetchone()
    assert fs2 == now1  # original
    assert ls2 == now2  # new timestamp
    assert title2 == "Engineer A (updated)"
    assert loc2 == "London, UK"
