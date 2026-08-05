"""
Tests for the Instagram scraper. Runs entirely against a saved HTML
fixture -- no live network/browser needed.
"""

from pathlib import Path

import pytest

from scrapers.instagram.scraper import InstagramScraper

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "instagram_profile_sample.html"


@pytest.mark.asyncio
async def test_scrape_returns_standardized_envelope():
    html = FIXTURE_PATH.read_text()
    scraper = InstagramScraper(job_id="test-job-1")

    result = await scraper.run({"username": "brightsmiledental", "fixture_html": html})

    assert result["scraper_type"] == "instagram"
    assert result["status"] == "completed"
    assert result["result_count"] == 1

    row = result["results"][0]
    assert set(row.keys()) == {"followers", "bio", "website", "email"}
    assert row["followers"] == 1234
    assert row["website"] == "https://brightsmile-example.com"
    assert row["email"] == "hello@brightsmile-example.com"
    assert "Dental clinic" in row["bio"]


@pytest.mark.asyncio
async def test_username_with_leading_at_symbol_is_stripped():
    html = FIXTURE_PATH.read_text()
    scraper = InstagramScraper(job_id="test-job-2")

    result = await scraper.run({"username": "@brightsmiledental", "fixture_html": html})

    assert result["status"] == "completed"
    assert result["source_query"]["username"] == "brightsmiledental"


@pytest.mark.asyncio
async def test_missing_username_fails_cleanly():
    scraper = InstagramScraper(job_id="test-job-3")
    result = await scraper.run({"username": "", "fixture_html": "<html></html>"})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_challenge_page_raises_blocked_error():
    scraper = InstagramScraper(job_id="test-job-4")
    challenge_html = '<html><body><div class="challenge-page"></div></body></html>'

    result = await scraper.run({"username": "someuser", "fixture_html": challenge_html})

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "blocked_or_captcha"


@pytest.mark.asyncio
async def test_profile_without_email_in_bio_returns_none():
    scraper = InstagramScraper(job_id="test-job-5")
    html = """
    <html><head>
    <meta name="description" content="Just a regular bio with no contact info." />
    <meta property="og:description" content="500 Followers, 10 Following, 5 Posts" />
    </head></html>
    """

    result = await scraper.run({"username": "someuser", "fixture_html": html})
    row = result["results"][0]

    assert row["followers"] == 500
    assert row["email"] is None
    assert row["website"] is None
