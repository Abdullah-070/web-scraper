"""
MongoDB persistence layer (per Intern 2's architecture decision).

Intern 2 (Node/Express + MongoDB) owns job creation and initial status
("pending"). This module is what Intern 3's worker uses to update status
to "running"/"completed"/"failed" and to write final results, per the
flow he described:

    1. Frontend -> Intern 2's API -> Mongo job doc created (status=pending)
    2. Intern 2 pushes {jobId, scraperType, inputParams} JSON onto a Redis list
    3. Intern 3's worker BRPOPs it, sets status=running
    4. Intern 3's worker scrapes, writes to Results collection,
       sets status=completed/failed

ASSUMPTIONS (flagged for confirmation with Intern 2 -- not yet confirmed):
- Database name: "sdip"
- Jobs collection: "jobs", keyed by a "jobId" field (string, not Mongo's
  own _id) so both sides can reference the same id without translating
  ObjectId <-> string.
- Results collection: "results", one document per completed job,
  referencing the same "jobId".
These are all defined as constants below -- if Intern 2's actual naming
differs, this is the only file that needs to change.
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
    """Update a job's status in the Jobs collection. Intern 2's API/frontend
    reads this to drive the dashboard's Pending/Running/Completed/Failed
    view (Sec 2.4 of the source doc).
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
    (see shared/schema.py) into the Results collection.
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
