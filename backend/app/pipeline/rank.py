from app.models import ValidatedProduct, ProfileSignals, RecommendedGift
from app.llm_client import call_llm_for_json

RANKING_SYSTEM_PROMPT = """You are ranking REAL, already-validated gift products for a professional contact.
You must choose ONLY from the numbered product list given to you.
Never invent a product, name, or URL that is not in the list.

Rules for Critical Ranking & Appropriateness:
1. STRICT CONFIDENCE SCORING RUBRIC:
   - 0.90 - 1.00: High-quality, premium product directly aligned with a specific, verified physical hobby or active personal interest (e.g., premium trail running flask for a trail runner, high-end chess set for a chess player).
   - 0.70 - 0.89: A relevant, high-quality workspace utility/accessory (e.g., wool felt desk mat) or a highly suitable book matched to their reading/professional topic.
   - 0.50 - 0.69: Universal, generic professional gift (e.g., high-quality notebook or steel tumbler) that is safe but has no strong personal customization.
   - Below 0.50: Loose, low-quality, or weak matches. If candidate products are poor, score them accordingly.
2. RISK LEVEL DEFINITIONS:
   - "high": Intimate/personal items (clothing, jewelry, fragrance, health products), or items matching `signals_to_avoid`. Avoid these entirely.
   - "medium": Consumables like food/beverages (unless profile explicitly indicates coffee/tea enthusiast), or opinionated business/political books, or bulky items that cause desk clutter.
   - "low": Universally accepted high-quality office stationery, organization tools, laptop accessories, or neutral professional development books.
3. GROUNDED REASONING:
   - `why_this_gift`: 1-2 professional sentences explaining the connection to their interests and how the product adds value, without sounding stalkerish or stating "I saw this on your profile".
   - `personalisation_reasoning`: Explain exactly which extracted profile signal(s) drove this pick.
4. QUANTITY CONSTRAINT: Choose up to 3 picks. If the candidate list is weak, generic, or mostly irrelevant, return fewer than 3 picks (even just 1 or 2) and assign low confidence scores.

Respond as JSON exactly matching this shape:
{
  "picks": [
    {
      "product_index": 0,
      "why_this_gift": "...",
      "personalisation_reasoning": "...",
      "confidence_score": 0.85,
      "risk_level": "low",
      "assumptions": ["..."]
    }
  ]
}
"""


def format_products_as_list(products: list[ValidatedProduct]) -> str:
    lines = []
    for index, product in enumerate(products):
        price = product.price_text or (f"~{product.price_value}" if product.price_value else "price unknown")
        lines.append(f"[{index}] {product.title} | {product.store} | {price} | relevance={product.relevance_score}")
    return "\n".join(lines)


def build_fallback_picks(candidates: list[ValidatedProduct]) -> list[dict]:
    return [
        {
            "product_index": i,
            "why_this_gift": "Selected by relevance score (LLM ranking unavailable).",
            "personalisation_reasoning": "Automatic fallback ranking — not LLM-reasoned.",
            "confidence_score": 0.3,
            "risk_level": "medium",
            "assumptions": ["LLM ranking step failed; using relevance score order as fallback"],
        }
        for i in range(min(3, len(candidates)))
    ]


def rank_top_gifts(
    candidates: list[ValidatedProduct],
    signals: ProfileSignals,
    currency: str,
) -> list[RecommendedGift]:
    if not candidates:
        return []

    product_list_text = format_products_as_list(candidates[:12])

    user_prompt = f"""Strong signals: {', '.join(signals.strong_signals) or 'none'}
Weak signals: {', '.join(signals.weak_signals) or 'none'}
Signals to avoid (NEVER use): {', '.join(signals.signals_to_avoid) or 'none'}

Candidate products:
{product_list_text}

Rank your top picks now."""

    try:
        result = call_llm_for_json(RANKING_SYSTEM_PROMPT, user_prompt, temperature=0.3)
        picks = result.get("picks", [])
    except (ValueError, Exception):
        picks = build_fallback_picks(candidates)

    ranked_gifts = []
    for rank_position, pick in enumerate(picks[:3], start=1):
        product_index = pick.get("product_index")

        if product_index is None or not (0 <= product_index < len(candidates)):
            continue

        chosen_product = candidates[product_index]

        ranked_gifts.append(RecommendedGift(
            rank=rank_position,
            gift_name=chosen_product.title,
            product_url=chosen_product.url,
            store=chosen_product.store,
            estimated_price=chosen_product.price_text or "Price unavailable — verify on store page",
            why_this_gift=pick.get("why_this_gift", ""),
            personalisation_reasoning=pick.get("personalisation_reasoning", ""),
            personalised_message="",
            confidence_score=float(pick.get("confidence_score", 0.5)),
            risk_level=pick.get("risk_level", "medium"),
            assumptions=pick.get("assumptions", []),
        ))

    return ranked_gifts
