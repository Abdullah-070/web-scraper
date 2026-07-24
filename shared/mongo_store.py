"""
ASSUMPTIONS :
- Database name: "sdip"
- Jobs collection: "jobs", keyed by a "jobId" field (string, not Mongo's
  own _id) so both sides can reference the same id without translating
  ObjectId <-> string.
- Results collection: "results", one document per completed job,
  referencing the same "jobId".
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "sdip")  # ASSUMPTION -- confirm with Intern 2

JOBS_COLLECTION = "jobs"  # ASSUMPTION -- confirm collection/field names
RESULTS_COLLECTION = "results"  # ASSUMPTION

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db():
    return get_client()[DB_NAME]


def set_job_status(job_id: str, status: str, extra: dict[str, Any] | None = None) -> None:
    """Update a job's status in the Jobs collection. I
    """
    db = get_db()
    update = {"status": status, "updated_at": datetime.now(timezone.utc)}
    if extra:
        update.update(extra)

    db[JOBS_COLLECTION].update_one(
        {"jobId": job_id},
        {"$set": update},
        upsert=True,  # upsert so this doesn't hard-fail if job doc doesn't exist yet
    )


def save_result(job_id: str, result_envelope: dict[str, Any]) -> None:
    """Write the scraper's standardized output envelope
    into the Results collection.
    """
    db = get_db()
    doc = dict(result_envelope)
    doc["jobId"] = job_id
    doc["saved_at"] = datetime.now(timezone.utc)

    db[RESULTS_COLLECTION].update_one(
        {"jobId": job_id},
        {"$set": doc},
        upsert=True,
    )
