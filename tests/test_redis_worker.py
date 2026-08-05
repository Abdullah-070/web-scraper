"""
Tests for workers.redis_worker.process_job.

Uses mongomock so these tests run without a live MongoDB or Redis
connection.
"""

from pathlib import Path

import mongomock
import pytest
from bson import ObjectId

from shared import mongo_store
from workers.redis_worker import process_job

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "linkedin_search_sample.html"


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """Replace the real MongoClient with mongomock for every test in this file."""
    fake_client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_store, "_client", fake_client)
    monkeypatch.setattr(mongo_store, "get_client", lambda: fake_client)
    yield fake_client


def _linkedin_payload(job_id: str, fixture_html: str) -> dict:
    return {
        "jobId": job_id,
        "scraperType": "linkedin",
        "inputParams": {
            "keywords": "marketing director",
            "location": "New York",
            "industry": "Software",
            "company_size": "51-200",
            "fixture_html": fixture_html,
            "auth": {"account_id": "test_account_1"},
        },
    }


@pytest.mark.asyncio
async def test_process_job_inserts_one_result_document_per_row(mock_mongo):
    """2 LinkedIn results in the fixture -> 2 separate Results documents,
    each shaped 
    """
    html = FIXTURE_PATH.read_text()
    db = mongo_store.get_db()

    user_id = ObjectId()
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": user_id, "status": "pending"}
    ).inserted_id
    job_id = str(job_id_obj)

    result = await process_job(_linkedin_payload(job_id, html))

    assert result["status"] == "completed"
    assert result["result_count"] == 2

    job_doc = db[mongo_store.JOBS_COLLECTION].find_one({"_id": job_id_obj})
    assert job_doc["status"] == "completed"

    result_docs = list(
        db[mongo_store.RESULTS_COLLECTION].find({"jobId": job_id_obj})
    )
    assert len(result_docs) == 2  # one document PER scraped row, not one for the whole job

    for doc in result_docs:
        assert isinstance(doc["jobId"], ObjectId)
        assert doc["jobId"] == job_id_obj
        assert doc["userId"] == user_id
        assert doc["scraperType"] == "linkedin"
        assert "name" in doc["data"]  # a single row's fields, not the whole envelope

    names = {doc["data"]["name"] for doc in result_docs}
    assert names == {"Jane Doe", "John Smith"}


@pytest.mark.asyncio
async def test_process_job_unknown_scraper_type_fails_cleanly(mock_mongo):
    db = mongo_store.get_db()
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": ObjectId(), "status": "pending"}
    ).inserted_id
    job_id = str(job_id_obj)

    payload = {"jobId": job_id, "scraperType": "not_a_real_scraper", "inputParams": {}}

    result = await process_job(payload)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "unknown_scraper_type"

    job_doc = db[mongo_store.JOBS_COLLECTION].find_one({"_id": job_id_obj})
    assert job_doc["status"] == "failed"

    # No results to insert for an unknown scraper type
    assert db[mongo_store.RESULTS_COLLECTION].count_documents({"jobId": job_id_obj}) == 0


@pytest.mark.asyncio
async def test_process_job_malformed_payload_missing_job_id(mock_mongo):
    result = await process_job({"scraperType": "linkedin"})
    assert result["status"] == "failed"
    assert result["error"] == "malformed_payload"


@pytest.mark.asyncio
async def test_process_job_invalid_object_id_fails_cleanly(mock_mongo):
    """A jobId that isn't a valid ObjectId must fail cleanly rather than crash the worker.
    """
    payload = _linkedin_payload("not-a-real-object-id", "irrelevant")

    result = await process_job(payload)

    assert result["status"] == "failed"
    assert result["errors"][0]["error_type"] == "invalid_input"


@pytest.mark.asyncio
async def test_process_job_missing_job_doc_saves_results_with_null_user_id(mock_mongo):
    
    html = FIXTURE_PATH.read_text()
    job_id = str(ObjectId())  # valid ObjectId format, but no job doc exists for it

    result = await process_job(_linkedin_payload(job_id, html))
    assert result["status"] == "completed"

    db = mongo_store.get_db()
    result_docs = list(
        db[mongo_store.RESULTS_COLLECTION].find({"jobId": ObjectId(job_id)})
    )
    assert len(result_docs) == 2
    assert all(doc["userId"] is None for doc in result_docs)


@pytest.mark.asyncio
async def test_process_job_google_maps_registered_and_wired(mock_mongo):
   
    gmaps_fixture = (
        Path(__file__).parent / "fixtures" / "google_maps_sample.html"
    ).read_text()
    db = mongo_store.get_db()
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": ObjectId(), "status": "pending"}
    ).inserted_id
    job_id = str(job_id_obj)

    payload = {
        "jobId": job_id,
        "scraperType": "google_maps",
        "inputParams": {
            "business_type": "dentist",
            "city": "Islamabad",
            "country": "Pakistan",
            "fixture_html": gmaps_fixture,
        },
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    assert result["result_count"] == 2

    result_docs = list(db[mongo_store.RESULTS_COLLECTION].find({"jobId": job_id_obj}))
    assert len(result_docs) == 2
    assert all(doc["scraperType"] == "google_maps" for doc in result_docs)


@pytest.mark.asyncio
async def test_process_job_website_registered_and_wired(mock_mongo, monkeypatch):
    
    import requests
    from unittest.mock import Mock

    mock_resp = Mock()
    mock_resp.text = "<html><body>contact us: hi@example.com</body></html>"
    mock_resp.status_code = 200
    mock_resp.headers = {}
    monkeypatch.setattr(requests, "get", lambda *a, **kw: mock_resp)

    db = mongo_store.get_db()
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": ObjectId(), "status": "pending"}
    ).inserted_id
    job_id = str(job_id_obj)

    payload = {
        "jobId": job_id,
        "scraperType": "website",
        "inputParams": {"website_url": "example.com"},
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    assert result["result_count"] == 1

    result_docs = list(db[mongo_store.RESULTS_COLLECTION].find({"jobId": job_id_obj}))
    assert len(result_docs) == 1
    assert result_docs[0]["data"]["emails"] == ["hi@example.com"]


@pytest.mark.asyncio
async def test_process_job_facebook_registered_and_wired(mock_mongo):
    
    fb_fixture = (
        Path(__file__).parent / "fixtures" / "facebook_page_sample.html"
    ).read_text()
    db = mongo_store.get_db()
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": ObjectId(), "status": "pending"}
    ).inserted_id
    job_id = str(job_id_obj)

    payload = {
        "jobId": job_id,
        "scraperType": "facebook",
        "inputParams": {
            "business_page": "brightsmiledental",
            "fixture_html": fb_fixture,
        },
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    assert result["result_count"] == 1

    result_docs = list(db[mongo_store.RESULTS_COLLECTION].find({"jobId": job_id_obj}))
    assert len(result_docs) == 1
    assert result_docs[0]["scraperType"] == "facebook"
    assert result_docs[0]["data"]["phone"] == "+925112345678"


@pytest.mark.asyncio
async def test_process_job_instagram_registered_and_wired(mock_mongo):
    
    ig_fixture = (
        Path(__file__).parent / "fixtures" / "instagram_profile_sample.html"
    ).read_text()
    db = mongo_store.get_db()
    job_id_obj = db[mongo_store.JOBS_COLLECTION].insert_one(
        {"userId": ObjectId(), "status": "pending"}
    ).inserted_id
    job_id = str(job_id_obj)

    payload = {
        "jobId": job_id,
        "scraperType": "instagram",
        "inputParams": {
            "username": "brightsmiledental",
            "fixture_html": ig_fixture,
        },
    }

    result = await process_job(payload)

    assert result["status"] == "completed"
    assert result["result_count"] == 1

    result_docs = list(db[mongo_store.RESULTS_COLLECTION].find({"jobId": job_id_obj}))
    assert len(result_docs) == 1
    assert result_docs[0]["scraperType"] == "instagram"
    assert result_docs[0]["data"]["followers"] == 1234
