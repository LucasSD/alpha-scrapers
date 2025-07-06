"""
test_qrt_scraper module
=======================

Unit and integration tests for the QrtScraper class in ``alpha_scrapers.qrt_scraper``.

Tests cover:
- Metadata extraction and job type parsing
- HTTP and JSON parsing logic
- Integration of the full run() pipeline
"""

import pytest

import alpha_scrapers.qrt_scraper as mod
from alpha_scrapers.qrt_scraper import QrtScraper
from tests.utils import FIXED_TS, DummyDateTime


@pytest.fixture(scope="module")
def scraper():
    """
    Fixture providing a QrtScraper instance for tests.

    :returns: QrtScraper instance
    :rtype: QrtScraper
    """
    return QrtScraper()


@pytest.mark.parametrize(
    "metadata,expected",
    [
        # Basic extraction
        (
            [{"name": "Experience (for job posting)", "value": "Students"}],
            "Students",
        ),
        # Case-insensitive match on name
        (
            [{"name": "experience (FOR JOB posting)", "value": "New Grads"}],
            "New Grads",
        ),
        # Metadata present but no matching entry
        (
            [{"name": "Other Field", "value": "X"}],
            "",
        ),
        # Empty metadata list
        (
            [],
            "",
        ),
        # No metadata key at all
        (
            None,
            "",
        ),
    ],
    ids=[
        "basic",
        "case_insensitive",
        "no_experience",
        "empty_list",
        "none_metadata",
    ],
)
def test_parse_job_type_various(scraper, metadata, expected):
    """
    Test parsing of job type from job metadata using QrtScraper.parse_job_type.

    :param scraper: QrtScraper instance
    :type scraper: QrtScraper
    :param metadata: Metadata list to test
    :type metadata: list[dict] or None
    :param expected: Expected job type string
    :type expected: str
    """
    job = {}
    if metadata is not None:
        job["metadata"] = metadata

    assert scraper.parse_job_type(job) == expected


def test_fetch_listings_page_delegates(scraper, monkeypatch):
    """
    Test that fetch_listings_page delegates to fetch_page with correct arguments.

    :param scraper: QrtScraper instance
    :type scraper: QrtScraper
    :param monkeypatch: pytest monkeypatch fixture
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    """
    dummy_data = {"jobs": []}
    called = {}

    def fake_fetch_page(url, params=None):
        called["url"] = url
        called["params"] = params
        return dummy_data

    monkeypatch.setattr(scraper, "fetch_page", fake_fetch_page)

    params = {"foo": "bar"}
    result = scraper.fetch_listings_page(params)

    assert result is dummy_data
    assert called["url"] == QrtScraper.BASE_URL
    assert called["params"] == params


def test_fetch_page_makes_http_call_and_parses(monkeypatch, scraper):
    """
    Test that fetch_page makes an HTTP call, parses JSON, and returns the data.

    :param monkeypatch: pytest monkeypatch fixture
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param scraper: QrtScraper instance
    :type scraper: QrtScraper
    """
    dummy_json = {"key": "value"}
    calls = {}

    class DummyResponse:
        def __init__(self, json_data, status_code=200):
            self._json = json_data
            self.status_code = status_code

        def raise_for_status(self):
            calls["raised"] = True

        def json(self):
            calls["parsed_json"] = True
            return self._json

    def fake_get(url, params=None):
        calls["url"] = url
        calls["params"] = params
        return DummyResponse(dummy_json)

    # Patch the session.get method
    monkeypatch.setattr(scraper.session, "get", fake_get)

    test_url = "http://example.com"
    test_params = {"a": "1"}
    data = scraper.fetch_page(test_url, test_params)

    # Ensure HTTP GET was called correctly
    assert calls["url"] == test_url
    assert calls["params"] == test_params
    # Ensure raise_for_status was invoked
    assert calls.get("raised") is True
    # Ensure json() was invoked
    assert calls.get("parsed_json") is True
    # Ensure returned object is the dummy JSON
    assert data == dummy_json


################################################################################
#                            INTEGRATION TEST: run()
################################################################################
@pytest.fixture(autouse=True)
def freeze_datetime(monkeypatch):
    """
    Monkeypatch datetime in the module so run() uses FIXED_TS for deterministic tests.

    :param monkeypatch: pytest monkeypatch fixture
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    """
    # Monkey-patch datetime in the module so run() uses FIXED_TS
    monkeypatch.setattr(mod, "datetime", DummyDateTime)


def test_run_produces_expected_records(monkeypatch, scraper):
    """
    Integration test for run(): verifies complete end-to-end job extraction and record structure.

    :param monkeypatch: pytest monkeypatch fixture
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param scraper: QrtScraper instance
    :type scraper: QrtScraper
    """

    # Stub out the listings JSON
    def job_template(job_id, title, loc, typ, url):
        return {
            "id": job_id,
            "absolute_url": url,
            "title": title,
            "location": {"name": loc},
            "metadata": [{"name": "Experience (for job posting)", "value": typ}],
        }

    url_a = "https://boards-api.greenhouse.io/jobs/A/1"
    url_b = "https://boards-api.greenhouse.io/jobs/B/2"
    dummy_listings = {
        "jobs": [
            job_template("J1", "Title A", "Loc A", "Type A", url_a),
            job_template(
                "", "Title B", "Loc B", "Type B", url_b
            ),  # missing id -> fallback
        ]
    }

    monkeypatch.setattr(
        scraper, "fetch_listings_page", lambda params=None: dummy_listings
    )

    # Run and verify
    results = scraper.run()
    expected = [
        {
            "url": url_a,
            "job_id": "J1",  # from id
            "title": "Title A",
            "location": "Loc A",
            "type": "Type A",
            "scraped_at": FIXED_TS,
        },
        {
            "url": url_b,
            "job_id": "2",  # fallback from URL path
            "title": "Title B",
            "location": "Loc B",
            "type": "Type B",
            "scraped_at": FIXED_TS,
        },
    ]

    results_sorted = sorted(results, key=lambda r: r["url"])
    expected_sorted = sorted(expected, key=lambda r: r["url"])
    assert results_sorted == expected_sorted
