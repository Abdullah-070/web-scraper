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


@pytest.mark.asyncio
async def test_mailto_and_tel_hrefs_extracted_even_without_visible_text(monkeypatch):
 
    icon_only_html = """
    <html><body>
      <a href="mailto:contact@example.com" aria-label="Email us"><svg></svg></a>
      <a href="tel:+15551234567" aria-label="Call us"><svg></svg></a>
    </body></html>
    """
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _mock_response(icon_only_html))

    scraper = WebsiteScraper(job_id="test-job-7")
    result = await scraper.run({"website_url": "https://example.com"})

    row = result["results"][0]
    assert row["emails"] == ["contact@example.com"]
    assert row["phone_numbers"] == ["+15551234567"]


@pytest.mark.asyncio
async def test_mailto_and_text_email_are_merged_without_duplicates(monkeypatch):
    html = """
    <html><body>
      <a href="mailto:hello@example.com">Email</a>
      <p>Or reach us at hello@example.com directly.</p>
      <p>Sales: sales@example.com</p>
    </body></html>
    """
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _mock_response(html))

    scraper = WebsiteScraper(job_id="test-job-8")
    result = await scraper.run({"website_url": "https://example.com"})

    row = result["results"][0]
    assert row["emails"] == ["hello@example.com", "sales@example.com"]


@pytest.mark.asyncio
async def test_contact_page_discovered_and_merged(monkeypatch):
    main_html = """
    <html><body>
      <p>Welcome to our site.</p>
      <a href="/contact-us">Contact Us</a>
    </body></html>
    """
    contact_html = """
    <html><body>
      <p>Email: sales@example.com</p>
      <a href="tel:+15559998888">Call</a>
    </body></html>
    """

    def fake_get(url, *a, **kw):
        if "contact" in url:
            return _mock_response(contact_html)
        return _mock_response(main_html)

    monkeypatch.setattr(requests, "get", fake_get)

    scraper = WebsiteScraper(job_id="test-job-9")
    result = await scraper.run({"website_url": "https://example.com"})

    row = result["results"][0]
    assert row["emails"] == ["sales@example.com"]
    assert row["phone_numbers"] == ["+15559998888"]


@pytest.mark.asyncio
async def test_fallback_contact_path_used_when_no_link_found(monkeypatch):
    main_html = "<html><body><p>No contact link here.</p></body></html>"
    contact_html = "<html><body><p>hello@example.com</p></body></html>"

    def fake_get(url, *a, **kw):
        if url.rstrip("/").endswith("/contact") or url.rstrip("/").endswith("/contact-us"):
            return _mock_response(contact_html)
        return _mock_response(main_html)

    monkeypatch.setattr(requests, "get", fake_get)

    scraper = WebsiteScraper(job_id="test-job-10")
    result = await scraper.run({"website_url": "https://example.com"})

    assert result["results"][0]["emails"] == ["hello@example.com"]


@pytest.mark.asyncio
async def test_contact_page_failure_does_not_crash_job(monkeypatch):
    main_html = '<html><body><a href="/contact">Contact</a></body></html>'

    def fake_get(url, *a, **kw):
        if "contact" in url:
            raise requests.exceptions.ConnectionError("boom")
        return _mock_response(main_html)

    monkeypatch.setattr(requests, "get", fake_get)

    scraper = WebsiteScraper(job_id="test-job-11")
    result = await scraper.run({"website_url": "https://example.com"})

    assert result["status"] == "completed"
    assert result["results"][0]["emails"] is None


@pytest.mark.asyncio
async def test_js_render_fallback_attempted_when_react_page_has_no_contact_info(monkeypatch):
   
    react_html = '<html><body><div id="root">React app shell, no static contact info</div></body></html>'
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _mock_response(react_html))

    scraper = WebsiteScraper(job_id="test-job-12")
    result = await scraper.run({"website_url": "https://example.com"})

    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_js_render_fallback_skipped_when_static_fetch_found_something(monkeypatch):
    react_html = '<html><body>Contact: hello@example.com <script>react</script></body></html>'
    monkeypatch.setattr(requests, "get", lambda *a, **kw: _mock_response(react_html))

    scraper = WebsiteScraper(job_id="test-job-13")
    result = await scraper.run({"website_url": "https://example.com"})

    assert result["results"][0]["emails"] == ["hello@example.com"]