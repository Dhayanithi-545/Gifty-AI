from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Experience(BaseModel):
    title: str
    company: str
    description: str = ""


class LinkedInProfile(BaseModel):
    headline: str = ""
    about: str = ""
    experience: list[Experience] = Field(default_factory=list)
    recent_posts: list[str] = Field(default_factory=list)
    recent_comments: list[str] = Field(default_factory=list)
    engaged_topics: list[str] = Field(default_factory=list)


class RelationshipContext(BaseModel):
    relationship_type: str = ""
    last_interaction: str = ""
    business_goal: str = ""


class GiftContext(BaseModel):
    occasion: str = ""
    budget_min: float = 0
    budget_max: float = 0
    currency: str = "INR"
    country: str = "India"
    tone: Literal["warm", "formal", "playful", "concise"] = "warm"


class ContactInput(BaseModel):
    name: str
    role: str = ""
    company: str = ""
    location: str = ""
    linkedin_profile: LinkedInProfile = Field(default_factory=LinkedInProfile)
    relationship_context: RelationshipContext = Field(default_factory=RelationshipContext)
    gift_context: GiftContext = Field(default_factory=GiftContext)


class ProfileSignals(BaseModel):
    strong_signals: list[str] = Field(default_factory=list)
    weak_signals: list[str] = Field(default_factory=list)
    signals_to_avoid: list[str] = Field(default_factory=list)


class GuardrailReport(BaseModel):
    blocked_terms_found: list[str] = Field(default_factory=list)
    signals_removed: list[str] = Field(default_factory=list)
    passed: bool = True


class SearchTrace(BaseModel):
    queries_used: list[str] = Field(default_factory=list)
    provider_used: Literal["serper", "duckduckgo", "none"] = "none"
    products_considered_count: int = 0
    fallback_triggered: bool = False


class RawProduct(BaseModel):
    title: str
    url: str
    price_text: str = ""
    price_value: Optional[float] = None
    store: str = ""
    source_query: str = ""


class ValidatedProduct(RawProduct):
    in_budget: bool = False
    relevance_score: float = 0.0
    rejection_reason: Optional[str] = None


class RecommendedGift(BaseModel):
    rank: int
    gift_name: str
    product_url: str
    store: str
    estimated_price: str
    why_this_gift: str
    personalisation_reasoning: str
    personalised_message: str
    confidence_score: float
    risk_level: Literal["low", "medium", "high"]
    assumptions: list[str] = Field(default_factory=list)


class HumanReview(BaseModel):
    status: Literal["pending_review", "approved", "rejected", "edited"] = "pending_review"
    available_actions: list[str] = Field(
        default_factory=lambda: ["approve", "reject", "edit", "regenerate"]
    )
    reviewer_note: Optional[str] = None


class ContactResult(BaseModel):
    contact_name: str
    profile_signals: ProfileSignals
    search_trace: SearchTrace
    recommended_gifts: list[RecommendedGift]
    human_review: HumanReview
    guardrail_report: GuardrailReport
    warnings: list[str] = Field(default_factory=list)


class RunRequest(BaseModel):
    contacts: list[ContactInput]


class RunResponse(BaseModel):
    results: list[ContactResult]


class ReviewActionRequest(BaseModel):
    contact_name: str
    action: Literal["approve", "reject", "edit", "regenerate"]
    edited_gift: Optional[RecommendedGift] = None
    reviewer_note: Optional[str] = None
