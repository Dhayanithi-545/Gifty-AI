import os
import re
import httpx
from app.models import RawProduct, SearchTrace
from app.llm_client import call_llm_for_json
from app.pipeline.guardrails import is_query_safe

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SERPER_SHOPPING_URL = "https://google.serper.dev/shopping"
SERPER_SEARCH_URL = "https://google.serper.dev/search"

QUERY_GENERATION_PROMPT = """You are the search-query generator inside Gifty, an AI
system that finds REAL, purchasable gifts for professional contacts (e.g. clients,
prospects, partners) based on their LinkedIn-style profile signals. Your only job is
to turn safe profile signals + a budget into search queries that will surface actual
products on Google Shopping or general web search — not advice articles, not listicles,
not gift-guide blog posts.

You will receive:
- strong_signals and weak_signals (safe, already-filtered interests/topics)
- budget_min, budget_max, currency, country

You must output 5-7 search queries as JSON. Nothing else.

═══════════════════════════════════════════
RULE 1 — NAME AN ACTUAL PRODUCT CATEGORY
═══════════════════════════════════════════
Every query must contain a concrete, physical product noun phrase a shopping
search engine can match against real listings.

GOOD: "leather notebook cover", "insulated coffee travel mug", "trail running belt"
BAD:  "thoughtful gift idea", "something nice for a colleague", "corporate gift"

═══════════════════════════════════════════
RULE 2 — BANNED WORDS (never output these in any query)
═══════════════════════════════════════════
gift, present, gifting, gift set, gift basket, gift idea, gift hamper,
for VP, for sales, for coworker, for client, for boss, corporate gift,
employee gift, business gift

These words pull up generic listicle/gimmick-store results instead of real
products. If your first instinct is to write "cricket gift for VP Sales",
strip it down to just "cricket bat" or "cricket book" instead.

═══════════════════════════════════════════
RULE 3 — NEVER PUT PRICE OR CURRENCY IN THE QUERY TEXT
═══════════════════════════════════════════
Do not write "under 2000 INR", "below $50", "budget gift", or any numeric/
currency token into the query string itself. Shopping search engines rank
worse on price-qualified queries. Budget is handled by RULE 4 instead —
through product TIER selection, not query text.

═══════════════════════════════════════════
RULE 4 — MAP BUDGET TO A PRODUCT TIER, NOT TO A PRICE STRING
═══════════════════════════════════════════
Convert budget_min/budget_max into one of these three tiers, then pick
product categories whose typical real-world price naturally lands there.
Use the worked examples below as your calibration — match the spirit of
quality level, not the literal example if a better fit exists.

TIER A — Everyday Premium  (~under 2,000 INR / under $30 / under €30)
  Pick small, well-made everyday items.
  Examples: "specialty coffee beans", "hardcover ruled notebook",
  "insulated stainless steel tumbler", "cable organizer desk clips",
  "scented candle gift tin", "premium ballpoint pen"

TIER B — Considered Upgrade  (~2,000-8,000 INR / $30-100 / €30-100)
  Pick durable, slightly aspirational workspace/hobby gear — the kind of
  thing someone would enjoy but might not buy for themselves on a whim.
  Examples: "leather journal cover", "pour over coffee dripper set",
  "wool felt desk mat", "hydration running vest", "bluetooth desk speaker",
  "wireless ergonomic mouse"

TIER C — Statement Quality  (~above 8,000 INR / above $100 / above €100)
  Pick recognisably high-end, heritage-feel, or precision-engineered items.
  Examples: "mechanical keyboard", "leather messenger bag",
  "noise cancelling headphones", "solid brass desk organizer set",
  "fountain pen gift box"

Compute the tier from the given budget_min/budget_max and currency BEFORE
writing any query. State your tier choice to yourself first, then generate
queries that match it.

═══════════════════════════════════════════
RULE 5 — THREE DISTINCT ANGLES (cover different signal types)
═══════════════════════════════════════════
If you have enough signal variety, generate exactly one query per angle below.
If signals only support 1-2 angles, it's fine to generate just 2 queries —
do not stretch a weak signal into a forced third angle.

  ANGLE 1 — Hobby/Interest: a product tied to their specific named hobby,
    sport, or personal interest from strong_signals.
    e.g. signal "enjoys cricket" → "cricket bat" / "cricket book"
    e.g. signal "trail running" → "trail running socks" / "hydration vest"

  ANGLE 2 — Workspace/Utility: a premium desk, office, or productivity item
    that fits any professional regardless of specific hobby.
    e.g. "ergonomic laptop riser", "leather pen case", "desk mat"

  ANGLE 3 — Reading/Learning: a specific book CATEGORY relevant to their
    role or stated professional interest — never a fabricated book title.
    e.g. role "VP Sales" → "sales leadership book"
    e.g. signal "distributed systems" → "distributed systems engineering book"

If strong_signals is empty or too thin to support Angle 1, skip it and
generate Angle 2 + Angle 3 only — do not invent a fake hobby to fill the gap.

═══════════════════════════════════════════
RULE 6 — APPEND COUNTRY CONTEXT
═══════════════════════════════════════════
End every query with "in {country}" so results are localised to real
shopping availability.
  e.g. "leather journal cover in India", "mechanical keyboard in USA"

═══════════════════════════════════════════
RULE 7 — FORMAT
═══════════════════════════════════════════
- 3 to 8 words per query, EXCLUDING the "in {country}" suffix
- No punctuation, no quotation marks, no operators (no AND/OR/site:/-)
- Plain, natural shopping-search phrasing — write it the way a real person
  would type into Google Shopping

═══════════════════════════════════════════
WORKED EXAMPLE
═══════════════════════════════════════════
Input:
  strong_signals: ["enjoys cricket", "SaaS sales leadership"]
  weak_signals: ["may appreciate business books"]
  budget_min: 3000, budget_max: 5000, currency: INR, country: India

Reasoning (internal, do not output): 3000-5000 INR → Tier B (Considered Upgrade).
Angle 1 from "enjoys cricket" → cricket gear. Angle 2 → workspace item at Tier B.
Angle 3 from "business books" weak signal → sales leadership book category.

Output:
{"queries": [
  "premium cricket bat in India",
  "leather desk organizer set in India",
  "sales leadership book in India"
]}

═══════════════════════════════════════════
OUTPUT
═══════════════════════════════════════════
Respond with ONLY this JSON shape, nothing before or after it:
{"queries": ["...", "...", "..."]}
"""


def generate_search_queries(
    strong_signals: list[str],
    weak_signals: list[str],
    budget_min: float,
    budget_max: float,
    currency: str,
    country: str,
) -> list[str]:
    all_signals = strong_signals + weak_signals
    signals_text = "; ".join(all_signals) or "general professional gift"

    user_prompt = (
        f"Signals: {signals_text}\n"
        f"Budget: {budget_min}-{budget_max} {currency}\n"
        f"Country: {country}\n"
        "Generate the search queries now."
    )

    try:
        result = call_llm_for_json(QUERY_GENERATION_PROMPT, user_prompt, temperature=0.4)
        queries = result.get("queries", [])
    except (ValueError, Exception):
        first_signal = (all_signals[0] if all_signals else "professional")
        queries = [f"professional gift {first_signal} under {budget_max} {currency} {country}"]

    safe_queries = [q for q in queries if is_query_safe(q)]

    if not safe_queries:
        safe_queries = [f"professional gift under {budget_max} {currency} {country}"]

# this line is respondible for getting number of queries
    return safe_queries[:3]


def parse_price_to_number(price_text: str) -> float | None:
    if not price_text:
        return None
    digits_only = re.sub(r"[^\d.]", "", price_text.replace(",", ""))
    try:
        return float(digits_only) if digits_only else None
    except ValueError:
        return None


def get_country_code(country: str) -> str:
    return "in" if "india" in country.lower() else "us"


def search_using_serper_shopping(query: str, country: str) -> list[RawProduct]:
    if not SERPER_API_KEY or SERPER_API_KEY == "your_serper_api_key_here":
        return []

    try:
        response = httpx.post(
            SERPER_SHOPPING_URL,
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": get_country_code(country)},
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return []

    products = []
    for item in data.get("shopping", [])[:8]:
        url = item.get("link", "")
        if not url:
            continue
        price_text = item.get("price", "")
        products.append(RawProduct(
            title=item.get("title", "Unknown product"),
            url=url,
            price_text=price_text,
            price_value=parse_price_to_number(price_text),
            store=item.get("source", "Unknown store"),
            source_query=query,
        ))

    return products


def search_using_serper_web(query: str, country: str) -> list[RawProduct]:
    if not SERPER_API_KEY or SERPER_API_KEY == "your_serper_api_key_here":
        return []

    try:
        response = httpx.post(
            SERPER_SEARCH_URL,
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query + " buy online", "gl": get_country_code(country)},
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return []

    products = []
    for item in data.get("organic", [])[:8]:
        url = item.get("link", "")
        if not url:
            continue
        domain = url.split("/")[2] if "//" in url else "Unknown"
        products.append(RawProduct(
            title=item.get("title", "Unknown product"),
            url=url,
            price_text="",
            price_value=None,
            store=item.get("source", domain),
            source_query=query,
        ))

    return products


def search_using_duckduckgo(query: str) -> list[RawProduct]:
    try:
        response = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query + " buy online"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15.0,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    matches = re.findall(
        r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>',
        response.text,
    )

    products = []
    for url, raw_title in matches[:8]:
        title = re.sub(r"<.*?>", "", raw_title).strip()
        if not title or not url.startswith("http"):
            continue
        domain = url.split("/")[2] if "//" in url else "Unknown"
        products.append(RawProduct(
            title=title,
            url=url,
            price_text="",
            price_value=None,
            store=domain,
            source_query=query,
        ))

    return products


def search_products(queries: list[str], country: str) -> tuple[list[RawProduct], SearchTrace]:
    all_products: list[RawProduct] = []
    provider_used = "none"
    fallback_triggered = False

    for query in queries:
        results = search_using_serper_shopping(query, country)
        if results:
            provider_used = "serper"
            all_products.extend(results)

    if not all_products:
        fallback_triggered = True
        for query in queries:
            results = search_using_serper_web(query, country)
            if results:
                provider_used = "serper"
                all_products.extend(results)

    if not all_products:
        for query in queries:
            results = search_using_duckduckgo(query)
            if results:
                provider_used = "duckduckgo"
                all_products.extend(results)

    trace = SearchTrace(
        queries_used=queries,
        provider_used=provider_used,
        products_considered_count=len(all_products),
        fallback_triggered=fallback_triggered,
    )

    return all_products, trace
