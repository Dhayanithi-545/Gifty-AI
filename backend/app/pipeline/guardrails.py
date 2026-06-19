import re
from app.models import ProfileSignals, GuardrailReport

SENSITIVE_CATEGORIES: dict[str, list[str]] = {
    "religion": [
        r"\b(hindu|muslim|christian|sikh|buddhist|jain|islam|temple|church|mosque|"
        r"gurudwara|prayer|fasting|ramadan|navratri|easter|religious|faith|god|"
        r"pilgrimage|halal|kosher)\b"
    ],
    "politics": [
        r"\b(bjp|congress party|aap\b|political party|election campaign|"
        r"vote for|politician|minister|parliament|modi|rahul gandhi|"
        r"political views|left-wing|right-wing|liberal politics|conservative politics)\b"
    ],
    "health": [
        r"\b(diagnosed|disease|cancer|diabetes|surgery|illness|medication|therapy session|"
        r"mental health|depression|anxiety disorder|disability|pregnan\w*|"
        r"hospitaliz\w*|medical condition|chronic|recovering from \w+ (surgery|illness))\b"
    ],
    "ethnicity": [
        r"\b(caste|ethnicity|race|tribal|brahmin|dalit|reservation category|"
        r"national origin|immigrant status)\b"
    ],
    "gender_identity": [
        r"\b(sexual orientation|gay|lesbian|transgender|non-binary|gender identity|lgbtq)\b"
    ],
    "family_status": [
        r"\b(divorce|married to|spouse name|my wife|my husband|my kids|my children|"
        r"single mother|single father|custody|widow|widower|trying to conceive)\b"
    ],
}

COMPILED_PATTERNS = {
    category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for category, patterns in SENSITIVE_CATEGORIES.items()
}


def find_sensitive_category(text: str) -> str | None:
    for category, patterns in COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return category
    return None


def filter_sensitive_signals(signals: list[str]) -> tuple[list[str], list[str], list[str]]:
    clean = []
    removed = []
    categories_found = []

    for signal in signals:
        category = find_sensitive_category(signal)
        if category:
            removed.append(signal)
            categories_found.append(category)
        else:
            clean.append(signal)

    return clean, removed, categories_found


def apply_guardrails(raw_signals: ProfileSignals) -> tuple[ProfileSignals, GuardrailReport]:
    clean_strong, removed_from_strong, categories_strong = filter_sensitive_signals(raw_signals.strong_signals)
    clean_weak, removed_from_weak, categories_weak = filter_sensitive_signals(raw_signals.weak_signals)

    all_removed = removed_from_strong + removed_from_weak
    all_categories = categories_strong + categories_weak

    clean_signals = ProfileSignals(
        strong_signals=clean_strong,
        weak_signals=clean_weak,
        signals_to_avoid=raw_signals.signals_to_avoid,
    )

    report = GuardrailReport(
        blocked_terms_found=list(set(all_categories)),
        signals_removed=all_removed,
        passed=len(all_removed) == 0,
    )

    return clean_signals, report


def is_query_safe(query: str) -> bool:
    return find_sensitive_category(query) is None
