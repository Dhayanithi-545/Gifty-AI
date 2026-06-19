from app.models import RecommendedGift, ContactInput
from app.llm_client import call_llm_for_text

TONE_DESCRIPTIONS = {
    "warm": "Warm, genuine, and personable — like a thoughtful colleague.",
    "formal": "Professional and polished — suitable for a senior executive relationship.",
    "playful": "Light, friendly, a little fun — but still appropriate for a business contact.",
    "concise": "Very short, 1-2 sentences max, no fluff.",
}

MESSAGE_SYSTEM_PROMPT = """You write short notes to accompany a professional gift.
Tone: {tone_description}

Rules for Accompanying Notes:
1. NATURAL INTEREST RECOGNITION: NEVER use phrases like "I saw on LinkedIn that you...", "I read your recent post where you...", or "I noticed you commented on...". Instead, weave the interest signal in a natural, friendly manner as if you knew it through general professional context (e.g., "Knowing your passion for trail running...", "As someone who appreciates premium workspace essentials...", "Given your interest in engineering leadership...").
2. FORBIDDEN WORDS & CLICHES: Avoid typical AI cliches and over-used corporate marketing fluff (e.g., "delve", "testament", "beacon", "unparalleled", "elevate", "nestled", "tapestry", "curated choice", "a small token of..."). Use simple, authentic, human-like phrasing.
3. OCCASION & RELATIONSHIP CONTEXT: Reference the specific occasion and relationship naturally. Ensure the note matches the professional boundary appropriate for the recipient.
4. CONTENT RESTRICTIONS: Never mention the price, the budget, or that the gift recommendation or message was AI-generated. Never reference sensitive personal attributes.
5. STRICT FORMATTING: Output ONLY the raw text of the note itself. Do NOT enclose the note in quotation marks. Do NOT add any sign-offs, salutations (e.g., "Best regards,"), signature blocks, or placeholder fields (e.g., "[Your Name]"). The user will sign the note themselves.
6. LENGTH: Write exactly 2-4 sentences (if tone is "concise", write only 1-2 sentences).
"""


def generate_personalised_message(contact: ContactInput, gift: RecommendedGift) -> str:
    tone = contact.gift_context.tone
    tone_description = TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["warm"])
    system_prompt = MESSAGE_SYSTEM_PROMPT.format(tone_description=tone_description)

    user_prompt = f"""Contact: {contact.name}
Occasion: {contact.gift_context.occasion}
Relationship: {contact.relationship_context.relationship_type}
Gift being sent: {gift.gift_name}
Why this gift fits: {gift.why_this_gift}

Write the accompanying note now."""

    try:
        return call_llm_for_text(system_prompt, user_prompt, temperature=0.6)
    except Exception:
        first_name = contact.name.split()[0]
        return (
            f"Hi {first_name}, just a small token of appreciation "
            f"following our recent conversation. Hope you enjoy it!"
        )
