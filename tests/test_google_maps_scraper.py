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
    
    scraper = GoogleMapsScraper(job_id="test-job-5")
    captcha_html = '<html><body><div class="g-recaptcha"></div></body></html>'

    result = await scraper.run(_valid_params(fixture_html=captcha_html))

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "blocked_or_captcha"


@pytest.mark.asyncio
async def test_max_results_caps_returned_rows():
    
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


@pytest.mark.asyncio
async def test_require_contact_info_filters_empty_rows():
    html = FIXTURE_PATH.read_text()
    scraper = GoogleMapsScraper(job_id="test-job-8")

    params = _valid_params(fixture_html=html)
    params["require_contact_info"] = True

    result = await scraper.run(params)

    
    assert all(r["phone"] or r["website"] for r in result["results"])


@pytest.mark.asyncio
async def test_require_contact_info_off_by_default():
    html = FIXTURE_PATH.read_text()
    scraper = GoogleMapsScraper(job_id="test-job-9")

    result = await scraper.run(_valid_params(fixture_html=html))

    assert result["result_count"] == 2  # both rows kept, filter not applied


@pytest.mark.asyncio
async def test_card_with_no_business_name_is_skipped():
    
    html = """
    <html><body>
    <div role="feed">
      <div>
        <div jsaction="empty1">
          <div class="fontHeadlineSmall"></div>
        </div>
      </div>
      <div>
        <div jsaction="real1">
          <div class="fontHeadlineSmall">Real Pharmacy</div>
          <span role="img" aria-label="4.0 stars 10 Reviews"></span>
        </div>
      </div>
    </div>
    </body></html>
    """
    scraper = GoogleMapsScraper(job_id="test-job-10")
    result = await scraper.run(_valid_params(fixture_html=html))

    assert result["result_count"] == 1
    assert result["results"][0]["business_name"] == "Real Pharmacy"


def test_reviews_text_pattern_matches_real_panel_text():
    
    import re

    from scrapers.google_maps.config import REVIEWS_TEXT_PATTERN

    panel_text = "Doctor's Pharmacy 4.0 4.0 stars 36 reviews Write a review Overview Reviews About"
    match = re.search(REVIEWS_TEXT_PATTERN, panel_text, re.IGNORECASE)

    assert match is not None
    assert match.group(1) == "36"


def test_reviews_text_pattern_handles_comma_thousands():
    import re

    from scrapers.google_maps.config import REVIEWS_TEXT_PATTERN

    match = re.search(REVIEWS_TEXT_PATTERN, "4.5 stars 1,234 reviews", re.IGNORECASE)
    assert match.group(1) == "1,234"


def test_reviews_text_pattern_handles_abbreviated_counts():
    
    import re

    from scrapers.google_maps.config import REVIEWS_TEXT_PATTERN
    from scrapers.google_maps.scraper import GoogleMapsScraper

    cases = [
        ("36 reviews", 36),
        ("1.2K reviews", 1200),
        ("3.4M reviews", 3400000),
        ("1,234 reviews", 1234),
    ]
    for text, expected in cases:
        match = re.search(REVIEWS_TEXT_PATTERN, text, re.IGNORECASE)
        assert match is not None, f"no match for {text!r}"
        assert GoogleMapsScraper._parse_review_count(match) == expected


def test_english_locale_forced_in_search_url():
    
    import inspect

    from scrapers.google_maps import scraper as gmaps_module

    source = inspect.getsource(gmaps_module)
    assert "hl=en" in source


def test_reviews_pattern_ignores_star_breakdown_aria_labels():
    
    import re

    from bs4 import BeautifulSoup

    from scrapers.google_maps.config import REVIEWS_TEXT_PATTERN

    real_snippet = (
        '<div class="PPCwl cYOgid"><div class="Bd93Zb"><table><tbody>'
        '<tr role="img" aria-label="5 stars, 4 reviews"><td>5</td></tr>'
        '<tr role="img" aria-label="1 stars, 1 review"><td>1</td></tr>'
        "</tbody></table></div>"
        '<div class="jANrlb"><div class="fontDisplayLarge">4.2</div>'
        '<button class="GQjSyb"><div class="HHrUdb"><span>5 reviews</span>'
        "</div></button></div></div>"
    )
    visible_text = BeautifulSoup(real_snippet, "html.parser").get_text(" ", strip=True)
    match = re.search(REVIEWS_TEXT_PATTERN, visible_text, re.IGNORECASE)

    assert match.group(1) == "5"  # the true total, not "4" from the breakdown row
