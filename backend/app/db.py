import os
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

# We use a JSON file for persistence, but we also hold everything in-memory.
DB_FILE = os.getenv("DATABASE_FILE", "gifty_db.json")

class ContactRecord(BaseModel):
    id: Optional[int] = None
    contact_name: str
    input_json: str
    result_json: str
    review_status: str = "pending_review"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReviewLog(BaseModel):
    id: Optional[int] = None
    contact_record_id: int
    action: str
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# In-memory storage structures
_contacts: Dict[str, ContactRecord] = {}
_review_logs: List[ReviewLog] = []
_next_contact_id: int = 1
_next_log_id: int = 1

def _load_db():
    global _contacts, _review_logs, _next_contact_id, _next_log_id
    if not os.path.exists(DB_FILE):
        _contacts = {}
        _review_logs = []
        _next_contact_id = 1
        _next_log_id = 1
        return

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            
            # Load contacts
            _contacts = {}
            for name, item in data.get("contacts", {}).items():
                created_at = datetime.fromisoformat(item["created_at"]) if "created_at" in item else datetime.now(timezone.utc)
                updated_at = datetime.fromisoformat(item["updated_at"]) if "updated_at" in item else datetime.now(timezone.utc)
                
                record = ContactRecord(
                    id=item.get("id"),
                    contact_name=item["contact_name"],
                    input_json=item["input_json"],
                    result_json=item["result_json"],
                    review_status=item.get("review_status", "pending_review"),
                    created_at=created_at,
                    updated_at=updated_at,
                )
                _contacts[name] = record
                if record.id and record.id >= _next_contact_id:
                    _next_contact_id = record.id + 1

            # Load logs
            _review_logs = []
            for item in data.get("review_logs", []):
                created_at = datetime.fromisoformat(item["created_at"]) if "created_at" in item else datetime.now(timezone.utc)
                log = ReviewLog(
                    id=item.get("id"),
                    contact_record_id=item["contact_record_id"],
                    action=item["action"],
                    note=item.get("note"),
                    created_at=created_at,
                )
                _review_logs.append(log)
                if log.id and log.id >= _next_log_id:
                    _next_log_id = log.id + 1
    except Exception as e:
        print(f"Error loading local DB file: {e}")
        # fallback to empty in case of corruption
        _contacts = {}
        _review_logs = []
        _next_contact_id = 1
        _next_log_id = 1

def _save_db():
    try:
        # Convert pydantic models to dicts and datetime to isoformat strings
        contacts_dict = {}
        for name, record in _contacts.items():
            contacts_dict[name] = {
                "id": record.id,
                "contact_name": record.contact_name,
                "input_json": record.input_json,
                "result_json": record.result_json,
                "review_status": record.review_status,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
            }
        
        logs_list = []
        for log in _review_logs:
            logs_list.append({
                "id": log.id,
                "contact_record_id": log.contact_record_id,
                "action": log.action,
                "note": log.note,
                "created_at": log.created_at.isoformat(),
            })

        data = {
            "contacts": contacts_dict,
            "review_logs": logs_list
        }
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving to local DB file: {e}")

def init_db():
    _load_db()

def save_contact_result(contact_dict: dict, result_dict: dict) -> int:
    global _next_contact_id
    name = contact_dict["name"]
    
    # Check if contact already exists
    existing = _contacts.get(name)
    if existing:
        existing.input_json = json.dumps(contact_dict)
        existing.result_json = json.dumps(result_dict)
        existing.review_status = result_dict.get("human_review", {}).get("status", "pending_review")
        existing.updated_at = datetime.now(timezone.utc)
        _save_db()
        return existing.id

    # Create new contact record
    new_id = _next_contact_id
    _next_contact_id += 1
    
    new_record = ContactRecord(
        id=new_id,
        contact_name=name,
        input_json=json.dumps(contact_dict),
        result_json=json.dumps(result_dict),
        review_status=result_dict.get("human_review", {}).get("status", "pending_review"),
    )
    _contacts[name] = new_record
    _save_db()
    return new_record.id

def fetch_all_contacts() -> list[dict]:
    return [json.loads(r.result_json) for r in _contacts.values()]

def fetch_contact_by_name(name: str) -> Optional[dict]:
    record = _contacts.get(name)
    return json.loads(record.result_json) if record else None

def fetch_contact_record_by_name(name: str) -> Optional[ContactRecord]:
    return _contacts.get(name)

def update_review_status(
    name: str,
    new_status: str,
    reviewer_note: Optional[str] = None,
    updated_gifts: Optional[dict] = None,
) -> bool:
    global _next_log_id
    record = _contacts.get(name)
    if not record:
        return False

    result_dict = json.loads(record.result_json)
    result_dict["human_review"]["status"] = new_status

    if reviewer_note:
        result_dict["human_review"]["reviewer_note"] = reviewer_note

    if updated_gifts:
        result_dict["recommended_gifts"] = updated_gifts.get(
            "recommended_gifts", result_dict["recommended_gifts"]
        )

    record.result_json = json.dumps(result_dict)
    record.review_status = new_status
    record.updated_at = datetime.now(timezone.utc)

    # Add audit log
    log_id = _next_log_id
    _next_log_id += 1
    audit_entry = ReviewLog(
        id=log_id,
        contact_record_id=record.id,
        action=new_status,
        note=reviewer_note,
    )
    _review_logs.append(audit_entry)
    _save_db()
    return True
