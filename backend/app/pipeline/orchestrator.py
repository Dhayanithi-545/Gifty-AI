from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from app.models import (
    ContactInput, ProfileSignals, GuardrailReport, SearchTrace,
    ValidatedProduct, RecommendedGift, ContactResult, HumanReview, RawProduct,
)
from app.pipeline.extract_signals import extract_profile_signals
from app.pipeline.guardrails import apply_guardrails
from app.pipeline.search import generate_search_queries, search_products
from app.pipeline.validate import validate_all_products, get_passing_products
from app.pipeline.rank import rank_top_gifts
from app.pipeline.message_gen import generate_personalised_message


class WorkflowState(TypedDict):
    contact: ContactInput
    raw_signals: Optional[ProfileSignals]
    clean_signals: Optional[ProfileSignals]
    guardrail_report: Optional[GuardrailReport]
    search_queries: list[str]
    search_trace: Optional[SearchTrace]
    raw_products: list[RawProduct]
    validated_products: list[ValidatedProduct]
    ranked_gifts: list[RecommendedGift]
    warnings: list[str]


def step_extract_signals(state: WorkflowState) -> WorkflowState:
    signals = extract_profile_signals(state["contact"])
    state["raw_signals"] = signals
    return state
                                                                
 
def step_apply_guardrails(state: WorkflowState) -> WorkflowState:
    clean_signals, report = apply_guardrails(state["raw_signals"])
    state["clean_signals"] = clean_signals
    state["guardrail_report"] = report

    if not report.passed:
        state["warnings"].append(
            f"Guardrails removed {len(report.signals_removed)} sensitive signal(s). "
            f"Categories blocked: {report.blocked_terms_found}"
        )

    return state


def step_generate_queries(state: WorkflowState) -> WorkflowState:
    gift_context = state["contact"].gift_context
    signals = state["clean_signals"]

    queries = generate_search_queries(
        strong_signals=signals.strong_signals,
        weak_signals=signals.weak_signals,
        budget_min=gift_context.budget_min,
        budget_max=gift_context.budget_max,
        currency=gift_context.currency,
        country=gift_context.country,
    )

    state["search_queries"] = queries
    return state


def step_search_products(state: WorkflowState) -> WorkflowState:
    products, trace = search_products(
        queries=state["search_queries"],
        country=state["contact"].gift_context.country,
    )

    state["search_trace"] = trace
    state["raw_products"] = products

    if trace.fallback_triggered:
        state["warnings"].append(
            "Primary search provider returned no results. Fallback search was used."
        )

    if trace.products_considered_count == 0:
        state["warnings"].append(
            "No products found by any search provider. "
            "This contact should be flagged for manual gift sourcing."
        )

    return state


def step_validate_products(state: WorkflowState) -> WorkflowState:
    gift_context = state["contact"].gift_context
    signals = state["clean_signals"]

    validated = validate_all_products(
        products=state["raw_products"],
        budget_min=gift_context.budget_min, 
        budget_max=gift_context.budget_max,
        strong_signals=signals.strong_signals,
        weak_signals=signals.weak_signals,
    )

    state["validated_products"] = validated

    passing = get_passing_products(validated)
    if not passing and validated:
        state["warnings"].append(
            "All candidate products failed validation checks. "
            "No gifts could be confidently recommended — human sourcing is recommended."
        )

    return state


def step_rank_gifts(state: WorkflowState) -> WorkflowState:
    passing_products = get_passing_products(state["validated_products"])

    gifts = rank_top_gifts(
        candidates=passing_products,
        signals=state["clean_signals"],
        currency=state["contact"].gift_context.currency,
    )

    state["ranked_gifts"] = gifts

    if not gifts:
        state["warnings"].append("Ranking step produced zero recommendations.")

    return state


def step_generate_messages(state: WorkflowState) -> WorkflowState:
    for gift in state["ranked_gifts"]:
        gift.personalised_message = generate_personalised_message(state["contact"], gift)
    return state


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("extract_signals", step_extract_signals)
    graph.add_node("apply_guardrails", step_apply_guardrails)
    graph.add_node("generate_queries", step_generate_queries)
    graph.add_node("search_products", step_search_products)
    graph.add_node("validate_products", step_validate_products)
    graph.add_node("rank_gifts", step_rank_gifts)
    graph.add_node("generate_messages", step_generate_messages)

    graph.set_entry_point("extract_signals")
    graph.add_edge("extract_signals", "apply_guardrails")
    graph.add_edge("apply_guardrails", "generate_queries")
    graph.add_edge("generate_queries", "search_products")
    graph.add_edge("search_products", "validate_products")
    graph.add_edge("validate_products", "rank_gifts")
    graph.add_edge("rank_gifts", "generate_messages")
    graph.add_edge("generate_messages", END)

    return graph.compile()


workflow = build_workflow_graph()


def run_workflow_for_contact(contact: ContactInput) -> ContactResult:
    initial_state: WorkflowState = {
        "contact": contact,
        "raw_signals": None,
        "clean_signals": None,
        "guardrail_report": None,
        "search_queries": [],
        "search_trace": None,
        "raw_products": [],
        "validated_products": [],
        "ranked_gifts": [],
        "warnings": [],
    }

    final_state = workflow.invoke(initial_state)

    return ContactResult(
        contact_name=contact.name,
        profile_signals=final_state["clean_signals"] or ProfileSignals(),
        search_trace=final_state["search_trace"] or SearchTrace(),
        recommended_gifts=final_state["ranked_gifts"],
        human_review=HumanReview(status="pending_review"),
        guardrail_report=final_state["guardrail_report"] or GuardrailReport(),
        warnings=final_state["warnings"],
    )


def regenerate_workflow_for_contact(contact: ContactInput) -> ContactResult:
    return run_workflow_for_contact(contact)
