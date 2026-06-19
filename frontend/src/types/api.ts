// TypeScript types matching the backend Pydantic models

export type Literal<T extends string> = T;

export interface Experience {
  title: string;
  company: string;
  description: string;
}

export interface LinkedInProfile {
  headline: string;
  about: string;
  experience: Experience[];
  recent_posts: string[];
  recent_comments: string[];
  engaged_topics: string[];
}

export interface RelationshipContext {
  relationship_type: string;
  last_interaction: string;
  business_goal: string;
}

export type Tone = "warm" | "formal" | "playful" | "concise";

export interface GiftContext {
  occasion: string;
  budget_min: number;
  budget_max: number;
  currency: string;
  country: string;
  tone: Tone;
}

export interface ContactInput {
  name: string;
  role: string;
  company: string;
  location: string;
  linkedin_profile: LinkedInProfile;
  relationship_context: RelationshipContext;
  gift_context: GiftContext;
}

export interface ProfileSignals {
  strong_signals: string[];
  weak_signals: string[];
  signals_to_avoid: string[];
}

export interface GuardrailReport {
  blocked_terms_found: string[];
  signals_removed: string[];
  passed: boolean;
}

export type ProviderUsed = "serper" | "duckduckgo" | "none";

export interface SearchTrace {
  queries_used: string[];
  provider_used: ProviderUsed;
  products_considered_count: number;
  fallback_triggered: boolean;
}

export interface RawProduct {
  title: string;
  url: string;
  price_text: string;
  price_value: number | null;
  store: string;
  source_query: string;
}

export interface ValidatedProduct extends RawProduct {
  in_budget: boolean;
  relevance_score: number;
  rejection_reason: string | null;
}

export type RiskLevel = "low" | "medium" | "high";

export interface RecommendedGift {
  rank: number;
  gift_name: string;
  product_url: string;
  store: string;
  estimated_price: string;
  why_this_gift: string;
  personalisation_reasoning: string;
  personalised_message: string;
  confidence_score: number;
  risk_level: RiskLevel;
  assumptions: string[];
}

export type ReviewStatus = "pending_review" | "approved" | "rejected" | "edited";

export interface HumanReview {
  status: ReviewStatus;
  available_actions: string[];
  reviewer_note: string | null;
}

export interface ContactResult {
  contact_name: string;
  profile_signals: ProfileSignals;
  search_trace: SearchTrace;
  recommended_gifts: RecommendedGift[];
  human_review: HumanReview;
  guardrail_report: GuardrailReport;
  warnings: string[];
}

export interface RunRequest {
  contacts: ContactInput[];
}

export interface RunResponse {
  results: ContactResult[];
}

export interface ReviewActionRequest {
  contact_name: string;
  action: "approve" | "reject" | "edit" | "regenerate";
  edited_gift?: RecommendedGift;
  reviewer_note?: string;
}

export interface HealthResponse {
  status: string;
  groq_key_configured: boolean;
  serper_key_configured: boolean;
  note: string | null;
}

export interface SavedProfile {
  id: string;
  name: string;
  contact: ContactInput;
  createdAt: string;
}
