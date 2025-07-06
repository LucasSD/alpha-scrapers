import pytest

from alpha_scrapers.qrt_scraper import QrtScraper


@pytest.fixture(scope="module")
def scraper():
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
    job = {}
    if metadata is not None:
        job["metadata"] = metadata

    assert scraper.parse_job_type(job) == expected


def test_fetch_listings_page_delegates(scraper, monkeypatch):
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
