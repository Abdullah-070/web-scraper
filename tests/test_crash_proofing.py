"""
Crash-proofing tests 
"""

import pytest

from scrapers.facebook.scraper import FacebookScraper
from scrapers.google_maps.scraper import GoogleMapsScraper
from scrapers.instagram.scraper import InstagramScraper
from scrapers.linkedin.scraper import LinkedInScraper
from scrapers.website.scraper import WebsiteScraper

GARBAGE_INPUTS = [
    {},
    {"totally": "unrelated", "keys": 123},
]


@pytest.mark.asyncio
@pytest.mark.parametrize("garbage", GARBAGE_INPUTS)
async def test_linkedin_never_crashes_on_garbage_input(garbage):
    scraper = LinkedInScraper(job_id="crash-test")
    result = await scraper.run(garbage)
    assert result["status"] == "failed"
    assert result["errors"]


@pytest.mark.asyncio
@pytest.mark.parametrize("garbage", GARBAGE_INPUTS)
async def test_google_maps_never_crashes_on_garbage_input(garbage):
    scraper = GoogleMapsScraper(job_id="crash-test")
    result = await scraper.run(garbage)
    assert result["status"] == "failed"
    assert result["errors"]


@pytest.mark.asyncio
@pytest.mark.parametrize("garbage", GARBAGE_INPUTS)
async def test_website_never_crashes_on_garbage_input(garbage):
    scraper = WebsiteScraper(job_id="crash-test")
    result = await scraper.run(garbage)
    assert result["status"] == "failed"
    assert result["errors"]


@pytest.mark.asyncio
@pytest.mark.parametrize("garbage", GARBAGE_INPUTS)
async def test_facebook_never_crashes_on_garbage_input(garbage):
    scraper = FacebookScraper(job_id="crash-test")
    result = await scraper.run(garbage)
    assert result["status"] == "failed"
    assert result["errors"]


@pytest.mark.asyncio
@pytest.mark.parametrize("garbage", GARBAGE_INPUTS)
async def test_instagram_never_crashes_on_garbage_input(garbage):
    scraper = InstagramScraper(job_id="crash-test")
    result = await scraper.run(garbage)
    assert result["status"] == "failed"
    assert result["errors"]


@pytest.mark.asyncio
async def test_linkedin_wrong_type_for_field_does_not_crash():
    """A field present but the wrong type 
    """
    scraper = LinkedInScraper(job_id="crash-test")
    result = await scraper.run(
        {
            "keywords": ["not", "a", "string"],
            "location": "New York",
            "industry": "Software",
            "company_size": "51-200",
            "auth": {"account_id": "test", "session_cookie": "x"},
        }
    )
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_website_wrong_type_for_url_does_not_crash():
    scraper = WebsiteScraper(job_id="crash-test")
    result = await scraper.run({"website_url": 12345})
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_google_maps_wrong_type_for_field_does_not_crash():
    scraper = GoogleMapsScraper(job_id="crash-test")
    result = await scraper.run(
        {"business_type": 123, "city": "Islamabad", "country": "Pakistan"}
    )
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_facebook_wrong_type_for_field_does_not_crash():
    scraper = FacebookScraper(job_id="crash-test")
    result = await scraper.run({"business_page": ["not", "a", "string"]})
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_instagram_wrong_type_for_field_does_not_crash():
    scraper = InstagramScraper(job_id="crash-test")
    result = await scraper.run({"username": {"nested": "dict"}})
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_process_job_survives_completely_empty_payload():
    """The worker's own entrypoint (not just the scraper) must survive
    an empty payload too.
    """
    from workers.redis_worker import process_job

    result = await process_job({})
    assert result["status"] == "failed"
    assert result.get("error") == "malformed_payload"
