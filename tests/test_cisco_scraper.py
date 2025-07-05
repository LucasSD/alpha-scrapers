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
