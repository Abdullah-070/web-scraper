"""
Tests for workers.redis_worker.process_job.

Uses mongomock so these tests run without a live MongoDB or Redis
connection -- mirrors the approach used for LinkedIn (fixture HTML
instead of a live account): test the logic in isolation from live
infrastructure.
"""

from pathlib import Path

import mongomock
import pytest

from shared import mongo_store
from workers.redis_worker import process_job

FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "linkedin_search_sample.html"
)


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """Replace the real MongoClient with mongomock for every test in this file."""
    fake_client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_store, "_client", fake_client)
    monkeypatch.setattr(mongo_store, "get_client", lambda: fake_client)
    yield fake_client


@pytest.mark.asyncio
async def test_process_job_updates_status_and_saves_result(mock_mongo):
    html = FIXTURE_PATH.read_text()
    payload = {
        "jobId": "job-abc-123",
        "scraperType": "linkedin",
        "inputParams": {
            "keywords": "marketing director",
            "location": "New York",
            "industry": "Software",
            "company_size": "51-200",
            "fixture_html": html,
            "auth": {"account_id": "test_account_1"},
        },
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    assert result["result_count"] == 2

    db = mongo_store.get_db()
    job_doc = db[mongo_store.JOBS_COLLECTION].find_one({"jobId": "job-abc-123"})
    assert job_doc["status"] == "completed"

    result_doc = db[mongo_store.RESULTS_COLLECTION].find_one({"jobId": "job-abc-123"})
    assert result_doc["result_count"] == 2
    assert result_doc["scraper_type"] == "linkedin"


@pytest.mark.asyncio
async def test_process_job_unknown_scraper_type_fails_cleanly(mock_mongo):
    payload = {
        "jobId": "job-xyz-999",
        "scraperType": "not_a_real_scraper",
        "inputParams": {},
    }

    result = await process_job(payload)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "unknown_scraper_type"

    db = mongo_store.get_db()
    job_doc = db[mongo_store.JOBS_COLLECTION].find_one({"jobId": "job-xyz-999"})
    assert job_doc["status"] == "failed"


@pytest.mark.asyncio
async def test_process_job_malformed_payload_missing_job_id(mock_mongo):
    result = await process_job({"scraperType": "linkedin"})
    assert result["status"] == "failed"
    assert result["error"] == "malformed_payload"
