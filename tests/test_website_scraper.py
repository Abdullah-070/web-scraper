"""
Tests for the Website scraper.

Mocks `requests.get` directly (via monkeypatch) rather than hitting any
live site -- no network calls happen during these tests.
"""

from unittest.mock import Mock

import pytest
import requests

from scrapers.website.scraper import WebsiteScraper

SAMPLE_HTML = """
<html>
<head><meta name="generator" content="WordPress 6.4"></head>
<body>
  <p>Contact us at hello@example.com or sales@example.com</p>
  <p>Call us: +92-51-1234567</p>
  <a href="https://facebook.com/examplebiz">Facebook</a>
  <a href="https://instagram.com/examplebiz">Instagram</a>
  <script src="https://cdn.shopify.com/somefile.js"></script>
</body>
</html>
"""


def _mock_response(html: str, status_code: int = 200, headers: dict | None = None):
    mock_resp = Mock()
    mock_resp.text = html
    mock_resp.status_code = status_code
    mock_resp.headers = headers or {}
    return mock_resp


@pytest.mark.asyncio
async def test_scrape_returns_standardized_envelope(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _mock_response(SAMPLE_HTML))

    scraper = WebsiteScraper(job_id="test-job-1")
    result = await scraper.run({"website_url": "example.com"})

    assert result["scraper_type"] == "website"
    assert result["status"] == "completed"
    assert result["result_count"] == 1

    row = result["results"][0]
    assert set(row.keys()) == {
        "emails",
        "phone_numbers",
        "social_links",
        "technologies_used",
    }
    assert row["emails"] == ["hello@example.com", "sales@example.com"]
    assert "https://facebook.com/examplebiz" in row["social_links"]
    assert "https://instagram.com/examplebiz" in row["social_links"]
    assert "Shopify" in row["technologies_used"]


@pytest.mark.asyncio
async def test_missing_url_fails_cleanly():
    scraper = WebsiteScraper(job_id="test-job-2")
    result = await scraper.run({"website_url": ""})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_malformed_url_fails_cleanly():
    scraper = WebsiteScraper(job_id="test-job-3")
    result = await scraper.run({"website_url": "not a url at all"})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_connection_error_fails_gracefully_without_crashing(monkeypatch):
    def raise_connection_error(*a, **kw):
        raise requests.exceptions.ConnectionError("DNS lookup failed")

    monkeypatch.setattr(requests, "get", raise_connection_error)

    scraper = WebsiteScraper(job_id="test-job-4")
    result = await scraper.run({"website_url": "https://this-domain-does-not-exist.invalid"})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "network_error"


@pytest.mark.asyncio
async def test_404_response_fails_gracefully(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: _mock_response("<html></html>", status_code=404)
    )

    scraper = WebsiteScraper(job_id="test-job-5")
    result = await scraper.run({"website_url": "https://example.com/missing-page"})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "network_error"


@pytest.mark.asyncio
async def test_page_with_no_contact_info_returns_all_none_fields(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: _mock_response("<html><body>Nothing here</body></html>")
    )

    scraper = WebsiteScraper(job_id="test-job-6")
    result = await scraper.run({"website_url": "https://example.com"})

    row = result["results"][0]
    assert row["emails"] is None
    assert row["phone_numbers"] is None
    assert row["social_links"] is None
    assert row["technologies_used"] is None
