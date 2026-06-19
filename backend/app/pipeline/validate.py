from app.models import RawProduct, ValidatedProduct

NON_PURCHASABLE_DOMAINS = [
    "wikipedia.org", "reddit.com", "quora.com", "youtube.com", "pinterest.com",
    "facebook.com", "instagram.com", "twitter.com", "x.com", "blogspot.com",
]

INAPPROPRIATE_KEYWORDS = [
    "lingerie", "alcohol", "wine bottle", "whisky", "cigarette", "weapon",
    "knife set", "tarot", "astrology", "religious idol", "political",
]


def extract_domain(url: str) -> str:
    try:
        return url.split("//")[1].split("/")[0].lower()
    except IndexError:
        return ""


def calculate_relevance_score(product_title: str, signals: list[str]) -> float:
    if not signals:
        return 0.3

    title_lower = product_title.lower()

    signal_words = set()
    for signal in signals:
        for word in signal.lower().split():
            if len(word) > 3:
                signal_words.add(word)

    if not signal_words:
        return 0.3

    matching_words = sum(1 for word in signal_words if word in title_lower)
    raw_score = matching_words / max(1, len(signal_words)) * 2

    return min(1.0, raw_score)


def validate_single_product(
    product: RawProduct,
    budget_min: float,
    budget_max: float,
    all_signals: list[str],
) -> ValidatedProduct:
    rejection_reason = None
    domain = extract_domain(product.url)

    if any(blocked in domain for blocked in NON_PURCHASABLE_DOMAINS):
        rejection_reason = f"Not a real purchasable storefront ({domain})"

    elif any(keyword in product.title.lower() for keyword in INAPPROPRIATE_KEYWORDS):
        rejection_reason = "Product category is inappropriate for professional gifting"

    elif product.price_value is not None and product.price_value > (budget_max * 1.2):
        rejection_reason = f"Price {product.price_value} exceeds budget limit of {budget_max}"

    relevance_score = calculate_relevance_score(product.title, all_signals)

    if rejection_reason is None and relevance_score < 0.1:
        rejection_reason = f"Product is not relevant to the contact's interests (score: {relevance_score:.2f})"

    in_budget = True
    if product.price_value is not None and product.price_value > budget_max:
        in_budget = False

    return ValidatedProduct(
        **product.model_dump(),
        in_budget=in_budget,
        relevance_score=round(relevance_score, 2),
        rejection_reason=rejection_reason,
    )


def validate_all_products(
    products: list[RawProduct],
    budget_min: float,
    budget_max: float,
    strong_signals: list[str],
    weak_signals: list[str],
) -> list[ValidatedProduct]:
    all_signals = strong_signals + weak_signals
    return [
        validate_single_product(product, budget_min, budget_max, all_signals)
        for product in products
    ]


def get_passing_products(validated_products: list[ValidatedProduct]) -> list[ValidatedProduct]:
    passed = [p for p in validated_products if p.rejection_reason is None]
    return sorted(passed, key=lambda p: p.relevance_score, reverse=True)
