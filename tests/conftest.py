import pytest

@pytest.fixture(autouse=True)
def patch_save_raw_response(monkeypatch):
    monkeypatch.setattr(
        "alpha_scrapers.alpha_scraper.AlphaScraper.save_raw_response",
        lambda self, content, filename: None
    ) 
