import os
import json
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Session, create_engine, select

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gifty.db")
engine = create_engine(DATABASE_URL, echo=False)


class ContactRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contact_name: str = Field(index=True)
    input_json: str
    result_json: str
    review_status: str = Field(default="pending_review", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contact_record_id: int = Field(index=True)
    action: str
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def init_db():
    SQLModel.metadata.create_all(engine)


def save_contact_result(contact_dict: dict, result_dict: dict) -> int:
    with Session(engine) as session:
        existing = session.exec(
            select(ContactRecord).where(ContactRecord.contact_name == contact_dict["name"])
        ).first()

        if existing:
            existing.input_json = json.dumps(contact_dict)
            existing.result_json = json.dumps(result_dict)
            existing.review_status = result_dict.get("human_review", {}).get("status", "pending_review")
            existing.updated_at = datetime.now(timezone.utc)
            session.add(existing)
            session.commit()
            return existing.id

        new_record = ContactRecord(
            contact_name=contact_dict["name"],
            input_json=json.dumps(contact_dict),
            result_json=json.dumps(result_dict),
            review_status=result_dict.get("human_review", {}).get("status", "pending_review"),
        )
        session.add(new_record)
        session.commit()
        session.refresh(new_record)
        return new_record.id


def fetch_all_contacts() -> list[dict]:
    with Session(engine) as session:
        records = session.exec(select(ContactRecord)).all()
        return [json.loads(r.result_json) for r in records]


def fetch_contact_by_name(name: str) -> Optional[dict]:
    with Session(engine) as session:
        record = session.exec(
            select(ContactRecord).where(ContactRecord.contact_name == name)
        ).first()
        return json.loads(record.result_json) if record else None


def fetch_contact_record_by_name(name: str) -> Optional[ContactRecord]:
    with Session(engine) as session:
        return session.exec(
            select(ContactRecord).where(ContactRecord.contact_name == name)
        ).first()


def update_review_status(
    name: str,
    new_status: str,
    reviewer_note: Optional[str] = None,
    updated_gifts: Optional[dict] = None,
) -> bool:
    with Session(engine) as session:
        record = session.exec(
            select(ContactRecord).where(ContactRecord.contact_name == name)
        ).first()

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
        session.add(record)

        audit_entry = ReviewLog(
            contact_record_id=record.id,
            action=new_status,
            note=reviewer_note,
        )
        session.add(audit_entry)
        session.commit()
        return True
