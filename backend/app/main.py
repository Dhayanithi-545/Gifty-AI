import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    RunRequest, RunResponse, ReviewActionRequest, ContactResult, ContactInput,
    ProfileSignals, SearchTrace, HumanReview, GuardrailReport,
)
from app.pipeline.orchestrator import run_workflow_for_contact, regenerate_workflow_for_contact
from app import db

app = FastAPI(
    title="Gifty",
    description="Hyper-personalised gift recommendation agent",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db.init_db()


@app.get("/")
def root():
    return {
        "message": "Gifty backend running successfully",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health_check():
    groq_configured = bool(GROQ_API_KEY := os.getenv("GROQ_API_KEY")) and GROQ_API_KEY != "your_groq_api_key_here"
    serper_configured = bool(SERPER_API_KEY := os.getenv("SERPER_API_KEY")) and SERPER_API_KEY != "your_serper_api_key_here"

    return {
        "status": "ok",
        "groq_key_configured": groq_configured,
        "serper_key_configured": serper_configured,
        "note": None if serper_configured else "Serper key not set — DuckDuckGo fallback will be used.",
    }


@app.post("/api/run", response_model=RunResponse)
def run_pipeline(request: RunRequest):
    if not request.contacts:
        raise HTTPException(status_code=400, detail="No contacts provided.")

    results: list[ContactResult] = []

    for contact in request.contacts:
        try:
            result = run_workflow_for_contact(contact)
        except Exception as error:
            result = ContactResult(
                contact_name=contact.name,
                profile_signals=ProfileSignals(),
                search_trace=SearchTrace(),
                recommended_gifts=[],
                human_review=HumanReview(),
                guardrail_report=GuardrailReport(),
                warnings=[f"Pipeline failed for this contact: {str(error)}"],
            )

        db.save_contact_result(contact.model_dump(), result.model_dump())
        results.append(result)

    return RunResponse(results=results)


@app.get("/api/contacts")
def list_all_contacts():
    return {"contacts": db.fetch_all_contacts()}


@app.get("/api/contacts/{name}")
def get_one_contact(name: str):
    result = db.fetch_contact_by_name(name)
    if not result:
        raise HTTPException(status_code=404, detail=f"No contact found with name '{name}'")
    return result


@app.post("/api/review")
def handle_review_action(request: ReviewActionRequest):
    record = db.fetch_contact_record_by_name(request.contact_name)
    if not record:
        raise HTTPException(status_code=404, detail=f"No contact found with name '{request.contact_name}'")

    if request.action == "regenerate":
        contact_data = json.loads(record.input_json)
        contact = ContactInput(**contact_data)
        new_result = regenerate_workflow_for_contact(contact)
        db.save_contact_result(contact.model_dump(), new_result.model_dump())
        return new_result

    if request.action == "edit":
        if not request.edited_gift:
            raise HTTPException(status_code=400, detail="'edit' action requires an 'edited_gift' in the request.")

        result_data = json.loads(record.result_json)
        gifts = result_data["recommended_gifts"]

        for index, gift in enumerate(gifts):
            if gift["rank"] == request.edited_gift.rank:
                gifts[index] = request.edited_gift.model_dump()
                break

        db.update_review_status(
            name=request.contact_name,
            new_status="edited",
            reviewer_note=request.reviewer_note,
            updated_gifts={"recommended_gifts": gifts},
        )
        return db.fetch_contact_by_name(request.contact_name)

    status_map = {"approve": "approved", "reject": "rejected"}
    new_status = status_map.get(request.action, request.action)

    db.update_review_status(
        name=request.contact_name,
        new_status=new_status,
        reviewer_note=request.reviewer_note,
    )
    return db.fetch_contact_by_name(request.contact_name)
