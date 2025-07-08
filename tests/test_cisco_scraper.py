"""
test_cisco_scraper module
========================

Unit and integration tests for the CiscoScraper class in ``alpha_scrapers.cisco_scraper``.

Tests cover:
- Job title and field extraction from HTML
- Job link extraction and deduplication
- HTTP and parsing logic
- Integration of the full run() pipeline
"""

import pytest
from bs4 import BeautifulSoup
from freezegun import freeze_time

from alpha_scrapers.cisco_scraper import CiscoScraper, LinkExtractionError


@pytest.fixture(scope="module")
def scraper():
    """
    Fixture providing a CiscoScraper instance for tests.

    :returns: CiscoScraper instance
    :rtype: CiscoScraper
    """
    return CiscoScraper()


@pytest.mark.parametrize(
    "html,expected",
    [
        # Basic title extraction
        ('<h2 class="title_page-1">Software Engineer</h2>', "Software Engineer"),
        # Leading/trailing whitespace should be stripped
        ("<h2 class='title_page-1'>  Data Analyst  </h2>", "Data Analyst"),
        # Missing class attribute: should return empty string
        ("<h2>No Class Here</h2>", ""),
        # Wrong tag: h1, not h2.title_page-1
        ("<h1 class='title_page-1'>Wrong Tag</h1>", ""),
        # Empty tag: no text
        ('<h2 class="title_page-1"></h2>', ""),
        # Only whitespace inside tag
        ('<h2 class="title_page-1">   \t</h2>', ""),
        # Multiple h2 tags: should pick the first one
        (
            '<h2 class="title_page-1">First</h2>'
            '<h2 class="title_page-1">Second</h2>',
            "First",
        ),
    ],
    ids=[
        "basic",
        "whitespace_trim",
        "missing_class",
        "wrong_tag",
        "empty",
        "only_whitespace",
        "multiple_tags",
    ],
)
def test_parse_job_title(html, expected, scraper):
    """
    Test extraction of job title from HTML using CiscoScraper.parse_job_title.

    :param html: HTML snippet containing job title
    :type html: str
    :param expected: Expected extracted title
    :type expected: str
    :param scraper: CiscoScraper instance
    :type scraper: CiscoScraper
    """
    soup = BeautifulSoup(html, "html.parser")
    assert scraper.parse_job_title(soup) == expected


@pytest.mark.parametrize(
    "html,label,expected",
    [
        # Basic field extraction
        (
            "<div>Job Id</div><div class='fields-data_value'>123</div>",
            "Job Id",
            "123",
        ),
        # Whitespace is trimmed
        (
            "<div>Job Id</div><div class='fields-data_value'>  ABC  </div>",
            "Job Id",
            "ABC",
        ),
        # Missing class on value div
        (
            "<div>Job Id</div><div>no class</div>",
            "Job Id",
            "",
        ),
        # Label not present
        (
            "<div>No Label</div><div class='fields-data_value'>XYZ</div>",
            "Job Id",
            "",
        ),
        # Multiple label/value pairs: return first
        (
            "<div>Job Id</div><div class='fields-data_value'>First</div>"
            "<div>Job Id</div><div class='fields-data_value'>Second</div>",
            "Job Id",
            "First",
        ),
    ],
    ids=[
        "basic",
        "whitespace",
        "no_value_class",
        "no_label",
        "multiple",
    ],
)
def test_parse_field(html, label, expected, scraper):
    """
    Test extraction of a field value from HTML using CiscoScraper.parse_field.

    :param html: HTML snippet containing field
    :type html: str
    :param label: Field label to search for
    :type label: str
    :param expected: Expected extracted value
    :type expected: str
    :param scraper: CiscoScraper instance
    :type scraper: CiscoScraper
    """
    soup = BeautifulSoup(html, "html.parser")
    assert scraper.parse_field(soup, label) == expected


def test_get_job_links_dedup_and_filter(scraper):
    """
    Test that get_job_links returns deduplicated and filtered job links.

    :param scraper: CiscoScraper instance
    :type scraper: CiscoScraper
    """
    html = """
    <table class="table_basic-1">
      <a href="/jobs/ProjectDetail/JobA/1">Job A</a>
      <a href="/jobs/ProjectDetail/JobB/2">Job B</a>
      <a href="/jobs/ProjectDetail/JobA/1">Job A dup</a>
      <a href="/jobs/OtherPage/3">Other</a>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    links = scraper.get_job_links(soup)
    expected = {
        "https://jobs.cisco.com/jobs/ProjectDetail/JobA/1",
        "https://jobs.cisco.com/jobs/ProjectDetail/JobB/2",
    }
    assert set(links) == expected
    assert len(links) == 2  # duplicates removed


def test_get_job_links_empty(scraper):
    """
    Test that get_job_links raises LinkExtractionError when no job links are found.

    :param scraper: CiscoScraper instance
    :type scraper: CiscoScraper
    """
    html = '<table class="table_basic-1"><a href="/jobs/Other/1">Other</a></table>'
    soup = BeautifulSoup(html, "html.parser")
    with pytest.raises(LinkExtractionError):
        scraper.get_job_links(soup)


def test_fetch_listings_page_delegates(scraper, monkeypatch):
    """
    Test that fetch_listings_page delegates to fetch_page with correct arguments.

    :param scraper: CiscoScraper instance
    :type scraper: CiscoScraper
    :param monkeypatch: pytest monkeypatch fixture
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    """
    dummy_soup = BeautifulSoup("<html></html>", "html.parser")
    called = {}

    def fake_fetch_page(url, params=None):
        called["url"] = url
        called["params"] = params
        return dummy_soup

    monkeypatch.setattr(scraper, "fetch_page", fake_fetch_page)
    params = {"foo": "bar"}
    result = scraper.fetch_listings_page(params)

    assert result is dummy_soup
    assert called["url"] == CiscoScraper.BASE_URL
    assert called["params"] == params


def test_fetch_page_makes_http_call_and_parses(monkeypatch, scraper):
    """
    Test that fetch_page makes an HTTP call, parses HTML, and returns BeautifulSoup.

    :param monkeypatch: pytest monkeypatch fixture
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param scraper: CiscoScraper instance
    :type scraper: CiscoScraper
    """
    html = "<div><span>TestContent</span></div>"
    calls = {}

    class DummyResponse:
        def __init__(self, text, status_code=200):
            self.text = text
            self.status_code = status_code

        def raise_for_status(self):
            calls["raised"] = True

    def fake_get(url, params=None):
        calls["url"] = url
        calls["params"] = params
        return DummyResponse(html)

    # Patch the session.get method
    monkeypatch.setattr(scraper.session, "get", fake_get)

    test_url = "http://example.com"
    test_params = {"a": "1"}
    soup = scraper.fetch_page(test_url, test_params)

    # Ensure HTTP GET was called correctly
    assert calls["url"] == test_url
    assert calls["params"] == test_params
    # Ensure raise_for_status was invoked
    assert calls.get("raised") is True
    # Ensure returned object is parsed HTML
    span = soup.find("span")
    assert span is not None and span.text == "TestContent"


################################################################################
#                            INTEGRATION TEST: run()
################################################################################


def make_job_soup(job_id, title, location, job_type):
    """
    Create a BeautifulSoup object representing a job detail page with given fields.

    :param job_id: Job identifier to embed.
    :type job_id: str
    :param title: Job title to embed.
    :type title: str
    :param location: Job location to embed.
    :type location: str
    :param job_type: Job type to embed.
    :type job_type: str
    :returns: Parsed HTML as BeautifulSoup.
    :rtype: BeautifulSoup
    """
    html = f"""
    <html><body>
      <h2 class="title_page-1">{title}</h2>
      <div>Job Id</div><div class="fields-data_value">{job_id}</div>
      <div>Location:</div><div class="fields-data_value">{location}</div>
      <div>Job Type</div><div class="fields-data_value">{job_type}</div>
    </body></html>
    """
    return BeautifulSoup(html, "html.parser")


@freeze_time("2025-07-06T12:00:00+00:00")
def test_run_produces_expected_records(monkeypatch, scraper):
    """
    Integration test for run(): verifies complete end-to-end job extraction and record structure.

    :param monkeypatch: Built-in pytest fixture for monkeypatching.
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param scraper: Fixture providing a CiscoScraper instance.
    :type scraper: CiscoScraper
    """
    # listings page with two links
    html_list = """
    <table class="table_basic-1">
      <a href="/jobs/ProjectDetail/A/1">A</a>
      <a href="/jobs/ProjectDetail/B/2">B</a>
    </table>
    """
    main_soup = BeautifulSoup(html_list, "html.parser")
    monkeypatch.setattr(
        scraper,
        "fetch_listings_page",
        lambda params=None, **kwargs: main_soup,
    )

    # per-URL job pages
    job_soups = {
        "https://jobs.cisco.com/jobs/ProjectDetail/A/1": make_job_soup(
            "A1", "Title A", "Loc A", "Type A"
        ),
        "https://jobs.cisco.com/jobs/ProjectDetail/B/2": make_job_soup(
            "B2", "Title B", "Loc B", "Type B"
        ),
    }

    monkeypatch.setattr(scraper, "fetch_page", lambda url, params=None, **kwargs: job_soups.get(url, main_soup))

    # run and assert
    results = scraper.run()
    expected = [
        {
            "url": "https://jobs.cisco.com/jobs/ProjectDetail/A/1",
            "job_id": "A1",
            "title": "Title A",
            "location": "Loc A",
            "type": "Type A",
            "scraped_at": "2025-07-06T12:00:00+00:00",
        },
        {
            "url": "https://jobs.cisco.com/jobs/ProjectDetail/B/2",
            "job_id": "B2",
            "title": "Title B",
            "location": "Loc B",
            "type": "Type B",
            "scraped_at": "2025-07-06T12:00:00+00:00",
        },
    ]
    results_sorted = sorted(results, key=lambda r: r["url"])
    expected_sorted = sorted(expected, key=lambda r: r["url"])
    assert results_sorted == expected_sorted
