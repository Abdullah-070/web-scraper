"""
End-to-end integration tests 
"""

from pathlib import Path
from unittest.mock import Mock

import mongomock
import pytest
import requests
from bson import ObjectId

from shared import mongo_store
from workers.redis_worker import process_job

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    fake_client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_store, "_client", fake_client)
    monkeypatch.setattr(mongo_store, "get_client", lambda: fake_client)
    yield fake_client


def _seed_job(db) -> tuple[ObjectId, str]:
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": ObjectId(), "status": "pending"}
    ).inserted_id
    return job_id_obj, str(job_id_obj)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scraper_type,input_params_fn,expected_min_results",
    [
        (
            "linkedin",
            lambda: {
                "keywords": "marketing director",
                "location": "New York",
                "industry": "Software",
                "company_size": "51-200",
                "fixture_html": (FIXTURES / "linkedin_search_sample.html").read_text(),
                "auth": {"account_id": "test_account_1"},
            },
            1,
        ),
        (
            "google_maps",
            lambda: {
                "business_type": "dentist",
                "city": "Islamabad",
                "country": "Pakistan",
                "fixture_html": (FIXTURES / "google_maps_sample.html").read_text(),
            },
            1,
        ),
        (
            "facebook",
            lambda: {
                "business_page": "brightsmiledental",
                "fixture_html": (FIXTURES / "facebook_page_sample.html").read_text(),
            },
            1,
        ),
        (
            "instagram",
            lambda: {
                "username": "brightsmiledental",
                "fixture_html": (FIXTURES / "instagram_profile_sample.html").read_text(),
            },
            1,
        ),
    ],
)
async def test_full_pipeline_for_each_scraper(
    mock_mongo, scraper_type, input_params_fn, expected_min_results
):
    """FR-4.1: job payload -> process_job -> scrape -> Mongo results ->
    job status = completed, for every browser-based scraper.
    """
    db = mongo_store.get_db()
    job_id_obj, job_id = _seed_job(db)

    payload = {
        "jobId": job_id,
        "scraperType": scraper_type,
        "inputParams": input_params_fn(),
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    assert result["result_count"] >= expected_min_results

    job_doc = db[mongo_store.JOBS_COLLECTION].find_one({"_id": job_id_obj})
    assert job_doc["status"] == "completed"

    result_docs = list(db[mongo_store.RESULTS_COLLECTION].find({"jobId": job_id_obj}))
    assert len(result_docs) == result["result_count"]
    assert all(doc["scraperType"] == scraper_type for doc in result_docs)


@pytest.mark.asyncio
async def test_full_pipeline_website_scraper(mock_mongo, monkeypatch):
    """Website scraper uses requests, not fixture_html -- tested separately."""
    mock_resp = Mock()
    mock_resp.text = "<html><body>contact: hi@example.com</body></html>"
    mock_resp.status_code = 200
    mock_resp.headers = {}
    monkeypatch.setattr(requests, "get", lambda *a, **kw: mock_resp)

    db = mongo_store.get_db()
    job_id_obj, job_id = _seed_job(db)

    payload = {
        "jobId": job_id,
        "scraperType": "website",
        "inputParams": {"website_url": "example.com"},
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    job_doc = db[mongo_store.JOBS_COLLECTION].find_one({"_id": job_id_obj})
    assert job_doc["status"] == "completed"


@pytest.mark.asyncio
async def test_all_five_scraper_types_are_registered():
    """Confirms the worker registry has exactly the 5 confirmed scrapers
    (per the scope decision that Yellow Pages/Yelp are out of scope) --
    catches accidental registry regressions.
    """
    from workers.redis_worker import _get_scraper_registry

    registry = _get_scraper_registry()
    assert set(registry.keys()) == {
        "linkedin",
        "google_maps",
        "website",
        "facebook",
        "instagram",
    }
