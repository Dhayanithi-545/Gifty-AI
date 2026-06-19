from app.models import ContactInput, ProfileSignals
from app.llm_client import call_llm_for_json

SYSTEM_PROMPT = """You are a professional-gifting signal analyst.

Given a contact's LinkedIn-style profile, extract gifting-relevant signals that can lead to high-quality, professional, and actionable physical gift searches.

Rules for Signal Types:
- strong_signals: Clear, specific, physical hobbies, sports, activities, or concrete product interests directly stated or repeatedly engaged with in the profile text (e.g., "cricket", "trail running", "pour-over coffee", "mechanical keyboards", "chess").
  *CRITICAL WARNING:* Abstract skills, business concepts, and professional roles (e.g., "SaaS GTM", "GTM leadership", "Revenue growth", "Software architecture", "mentorship", "management") are NOT actionable gifting signals. NEVER put abstract skills or buzzwords here.
- weak_signals: Plausible, less certain interests, or professional topics translated into physical gift categories.
  *For professional topics:* If the user is only posting about "engineering management" or "SaaS GTM", translate this into "books on engineering leadership" or "business strategy literature".
  *Universal options:* If there are no personal hobbies or interests stated, use high-quality professional essentials like "premium desk organization", "ergonomic workspace accessories", "high-end writing instruments", or "leather journals".
- signals_to_avoid: Any sensitive profile mentions touching religion, politics, health conditions/medical details, ethnicity, gender identity, or family/marital status. List these explicitly here for auditing, and never use them in other fields.

Gifting Signal Extraction Rules:
- Never invent interests that are not directly supported by the profile text.
- Do not extract vague, generic terms like "technology", "finance", "business", or "marketing". Be specific (e.g., "reading books on tech history", "minimalist desk accessories").
- Output 2-6 strong_signals, 0-4 weak_signals, and 0-5 signals_to_avoid.

Respond as JSON exactly matching this shape:
{
  "strong_signals": ["..."],
  "weak_signals": ["..."],
  "signals_to_avoid": ["..."]
}
"""


def build_profile_prompt(contact: ContactInput) -> str:
    profile = contact.linkedin_profile

    experience_lines = "\n".join(
        f"- {exp.title} at {exp.company}: {exp.description}"
        for exp in profile.experience
    )

    posts_text = "\n".join(f"- {post}" for post in profile.recent_posts)
    comments_text = "\n".join(f"- {comment}" for comment in profile.recent_comments)
    topics_text = ", ".join(profile.engaged_topics)

    return f"""Contact: {contact.name}
Role: {contact.role} at {contact.company}
Location: {contact.location}

Headline: {profile.headline}
About: {profile.about}

Experience:
{experience_lines or "(none provided)"}

Recent posts:
{posts_text or "(none provided)"}

Recent comments:
{comments_text or "(none provided)"}

Engaged topics: {topics_text or "(none provided)"}

Extract gifting signals per the rules above."""


def extract_profile_signals(contact: ContactInput) -> ProfileSignals:
    user_prompt = build_profile_prompt(contact)

    try:
        result = call_llm_for_json(SYSTEM_PROMPT, user_prompt, temperature=0.2)
        return ProfileSignals(
            strong_signals=result.get("strong_signals", [])[:6],
            weak_signals=result.get("weak_signals", [])[:4],
            signals_to_avoid=result.get("signals_to_avoid", [])[:5],
        )
    except (ValueError, Exception):
        return ProfileSignals(
            strong_signals=[],
            weak_signals=[contact.role] if contact.role else [],
            signals_to_avoid=["Signal extraction failed — manual review recommended"],
        )
