import pytest
from bs4 import BeautifulSoup

from alpha_scrapers.cisco_scraper import CiscoScraper


@pytest.fixture(scope="module")
def scraper():
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
    soup = BeautifulSoup(html, "html.parser")
    assert scraper.parse_field(soup, label) == expected


def test_get_job_links_dedup_and_filter(scraper):
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
    html = '<table class="table_basic-1"><a href="/jobs/Other/1">Other</a></table>'
    soup = BeautifulSoup(html, "html.parser")
    assert scraper.get_job_links(soup) == []
