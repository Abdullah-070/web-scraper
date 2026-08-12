"""
Tests for the Google Maps scraper.

Runs entirely against the saved HTML fixture (no live network/browser).
"""

from pathlib import Path

import pytest

from scrapers.google_maps.scraper import GoogleMapsScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "google_maps_sample.html"


def _valid_params(fixture_html: str | None = None) -> dict:
    return {
        "business_type": "dentist",
        "city": "Islamabad",
        "country": "Pakistan",
        "fixture_html": fixture_html,
    }


@pytest.mark.asyncio
async def test_scrape_returns_standardized_envelope():
    html = FIXTURE_PATH.read_text()
    scraper = GoogleMapsScraper(job_id="test-job-1")

    result = await scraper.run(_valid_params(fixture_html=html))

    assert result["scraper_type"] == "google_maps"
    assert result["status"] == "completed"
    assert result["result_count"] == 2
    assert result["errors"] == []

    row = result["results"][0]
    assert set(row.keys()) == {
        "business_name",
        "phone",
        "email",
        "website",
        "address",
        "rating",
        "reviews",
    }
    assert row["business_name"] == "Bright Smile Dental"
    assert row["address"] == "Blue Area, Islamabad"
    assert row["website"] == "https://brightsmile-example.com"
    assert row["phone"] == "+92-51-1234567"
    assert row["rating"] == 4.5
    assert row["reviews"] == 123
    assert row["email"] is None  # not exposed by Google Maps directly


@pytest.mark.asyncio
async def test_second_row_without_website_has_none():
    html = FIXTURE_PATH.read_text()
    scraper = GoogleMapsScraper(job_id="test-job-2")

    result = await scraper.run(_valid_params(fixture_html=html))
    second_row = result["results"][1]

    assert second_row["business_name"] == "Islamabad Family Dentist"
    assert second_row["website"] is None
    assert second_row["rating"] == 4.0
    assert second_row["reviews"] == 56


@pytest.mark.asyncio
async def test_missing_required_field_fails_cleanly():
    scraper = GoogleMapsScraper(job_id="test-job-3")
    params = _valid_params(fixture_html="<html></html>")
    del params["city"]

    result = await scraper.run(params)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_empty_results_page_returns_completed_with_zero_rows():
    scraper = GoogleMapsScraper(job_id="test-job-4")
    empty_html = "<html><body><div role='feed'></div></body></html>"

    result = await scraper.run(_valid_params(fixture_html=empty_html))

    assert result["status"] == "completed"
    assert result["result_count"] == 0
    assert result["results"] == []


@pytest.mark.asyncio
async def test_recaptcha_page_raises_blocked_error():
    """Week 3: confirms Google Maps now uses the shared CAPTCHA detection
    utility, same as LinkedIn/Facebook/Instagram (NFR-3.1).
    """
    scraper = GoogleMapsScraper(job_id="test-job-5")
    captcha_html = '<html><body><div class="g-recaptcha"></div></body></html>'

    result = await scraper.run(_valid_params(fixture_html=captcha_html))

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "blocked_or_captcha"


@pytest.mark.asyncio
async def test_max_results_caps_returned_rows():
    """Post-launch fix: results are now capped deterministically instead
    of varying by how much the feed happened to scroll-load (Intern 2's
    'inconsistent entry counts' report).
    """
    html = FIXTURE_PATH.read_text()
    scraper = GoogleMapsScraper(job_id="test-job-6")

    params = _valid_params(fixture_html=html)
    params["max_results"] = 1

    result = await scraper.run(params)

    assert result["status"] == "completed"
    assert result["result_count"] == 1
    assert result["results"][0]["business_name"] == "Bright Smile Dental"


@pytest.mark.asyncio
async def test_invalid_max_results_fails_cleanly():
    scraper = GoogleMapsScraper(job_id="test-job-7")
    params = _valid_params(fixture_html="<html></html>")
    params["max_results"] = "not-a-number"

    result = await scraper.run(params)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"
