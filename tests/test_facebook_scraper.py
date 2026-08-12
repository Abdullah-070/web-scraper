"""
Tests for the Facebook scraper. Runs entirely against a saved HTML
fixture -- no live network/browser needed.
"""

from pathlib import Path

import pytest

from scrapers.facebook.scraper import FacebookScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "facebook_page_sample.html"


@pytest.mark.asyncio
async def test_scrape_returns_standardized_envelope():
    html = FIXTURE_PATH.read_text()
    scraper = FacebookScraper(job_id="test-job-1")

    result = await scraper.run(
        {"business_page": "brightsmiledental", "fixture_html": html}
    )

    assert result["scraper_type"] == "facebook"
    assert result["status"] == "completed"
    assert result["result_count"] == 1

    row = result["results"][0]
    assert set(row.keys()) == {"contact_info", "website", "phone"}
    assert row["phone"] == "+92 51 1234 5678"
    assert row["website"] == "https://brightsmile-example.com"
    assert "Bright Smile Dental Clinic" in row["contact_info"]
    
    assert "facebook.com" not in row["website"]
    assert "fbcdn.net" not in row["website"]


@pytest.mark.asyncio
async def test_missing_business_page_fails_cleanly():
    scraper = FacebookScraper(job_id="test-job-2")
    result = await scraper.run({"business_page": "", "fixture_html": "<html></html>"})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_checkpoint_page_raises_blocked_error():
    scraper = FacebookScraper(job_id="test-job-3")
    checkpoint_html = '<html><body><button id="checkpointSubmitButton"></button></body></html>'

    result = await scraper.run(
        {"business_page": "somepage", "fixture_html": checkpoint_html}
    )

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "blocked_or_captcha"


@pytest.mark.asyncio
async def test_generic_keyword_block_detected():
    
    scraper = FacebookScraper(job_id="test-job-4")
    block_html = "<html><body><p>Unusual traffic detected from your network.</p></body></html>"

    result = await scraper.run(
        {"business_page": "somepage", "fixture_html": block_html}
    )

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "blocked_or_captcha"


@pytest.mark.asyncio
async def test_page_with_no_contact_info_returns_none_fields():
    scraper = FacebookScraper(job_id="test-job-5")
    empty_html = "<html><body><p>Just some page content.</p></body></html>"

    result = await scraper.run(
        {"business_page": "somepage", "fixture_html": empty_html}
    )

    row = result["results"][0]
    assert row["phone"] is None
    assert row["website"] is None
    assert row["contact_info"] is None


@pytest.mark.asyncio
async def test_tel_link_preferred_over_regex_when_present():
   
    scraper = FacebookScraper(job_id="test-job-6")
    html_with_tel = """
    <html><body>
    <a href="tel:+925199998888">Call us</a>
    <p>Some other number mentioned: +92 51 1234 5678 in the text.</p>
    </body></html>
    """

    result = await scraper.run(
        {"business_page": "somepage", "fixture_html": html_with_tel}
    )

    row = result["results"][0]
    assert row["phone"] == "+925199998888"


@pytest.mark.asyncio
async def test_phone_found_in_body_when_meta_has_no_phone():
    scraper = FacebookScraper(job_id="test-job-7")
    html = """
    <html>
    <head><meta property="og:description" content="Dentist in Islamabad. Open daily." /></head>
    <body><p>Call us at +92 51 1234 5678 for appointments.</p></body>
    </html>
    """

    result = await scraper.run({"business_page": "somepage", "fixture_html": html})
    row = result["results"][0]

    assert row["phone"] == "+92 51 1234 5678"
    assert row["contact_info"] == "Dentist in Islamabad. Open daily."
