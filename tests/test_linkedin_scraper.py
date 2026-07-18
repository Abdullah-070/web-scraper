"""
Tests for the LinkedIn scraper.

Per mentor decision, no personal/real LinkedIn account is ever used in
testing. All tests here run against the saved HTML fixture
(tests/fixtures/linkedin_search_sample.html) via the `fixture_html` param,
which bypasses both the network call and the auth requirement.
"""

from pathlib import Path

import pytest

from scrapers.linkedin.scraper import LinkedInScraper
from shared.exceptions import InvalidInputError, AuthenticationError

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "linkedin_search_sample.html"


def _valid_params(fixture_html: str | None = None) -> dict:
    return {
        "keywords": "marketing director",
        "location": "New York",
        "industry": "Software",
        "company_size": "51-200",
        "fixture_html": fixture_html,
        "auth": {"account_id": "test_account_1"},
    }


@pytest.mark.asyncio
async def test_scrape_returns_standardized_envelope():
    html = FIXTURE_PATH.read_text()
    scraper = LinkedInScraper(job_id="test-job-1")

    result = await scraper.run(_valid_params(fixture_html=html))

    assert result["scraper_type"] == "linkedin"
    assert result["status"] == "completed"
    assert result["result_count"] == 2
    assert result["errors"] == []

    row = result["results"][0]
    # every field in RESULT_FIELDS must be present, even if None
    assert set(row.keys()) == {
        "name",
        "company",
        "position",
        "profile_url",
        "email",
        "website",
    }
    assert row["name"] == "Jane Doe"
    assert row["position"] == "Marketing Director"
    assert row["company"] == "Acme Corp"
    assert "linkedin.com/in/jane-doe-example" in row["profile_url"]


@pytest.mark.asyncio
async def test_missing_required_field_fails_cleanly():
    scraper = LinkedInScraper(job_id="test-job-2")
    params = _valid_params(fixture_html="<html></html>")
    del params["location"]

    result = await scraper.run(params)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_missing_auth_and_no_fixture_fails_with_auth_error():
    scraper = LinkedInScraper(job_id="test-job-3")
    params = _valid_params(fixture_html=None)
    params["auth"] = {}

    result = await scraper.run(params)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "authentication_error"


@pytest.mark.asyncio
async def test_captcha_page_raises_blocked_error():
    scraper = LinkedInScraper(job_id="test-job-4")
    captcha_html = '<html><body><div id="captcha-internal"></div></body></html>'

    result = await scraper.run(_valid_params(fixture_html=captcha_html))

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "blocked_or_captcha"


@pytest.mark.asyncio
async def test_empty_results_page_returns_completed_with_zero_rows():
    scraper = LinkedInScraper(job_id="test-job-5")
    empty_html = "<html><body></body></html>"

    result = await scraper.run(_valid_params(fixture_html=empty_html))

    assert result["status"] == "completed"
    assert result["result_count"] == 0
    assert result["results"] == []


@pytest.mark.asyncio
async def test_missing_account_id_in_live_mode_is_rejected():
    """A real (non-fixture) job with a session cookie but no account_id
    must fail validation rather than silently sharing a rate-limit bucket
    with other unrelated jobs (FR-1.9).
    """
    scraper = LinkedInScraper(job_id="test-job-6")
    params = {
        "keywords": "marketing director",
        "location": "New York",
        "industry": "Software",
        "company_size": "51-200",
        "auth": {"session_cookie": "fake-cookie-value"},  # no account_id
    }

    result = await scraper.run(params)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"
    assert "account_id" in result["errors"][0]["message"]
