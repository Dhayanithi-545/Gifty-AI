import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_llm(temperature: float = 0.3) -> ChatGroq:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add your free key from "
            "https://console.groq.com/keys to your .env file."
        )
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=temperature,
    )


def remove_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def call_llm_for_json(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> dict:
    llm = get_llm(temperature=temperature)

    strict_system = (
        system_prompt
        + "\n\nIMPORTANT: Respond with ONLY a valid JSON object. "
        "No markdown, no explanation outside the JSON."
    )

    messages = [("system", strict_system), ("human", user_prompt)]
    response = llm.invoke(messages)
    cleaned = remove_markdown_fences(response.content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        retry_messages = [
            ("system", strict_system),
            ("human", user_prompt),
            ("assistant", cleaned),
            ("human", "That was not valid JSON. Reply with ONLY the corrected JSON object."),
        ]
        retry_response = llm.invoke(retry_messages)
        cleaned_retry = remove_markdown_fences(retry_response.content)
        try:
            return json.loads(cleaned_retry)
        except json.JSONDecodeError as error:
            raise ValueError(f"LLM could not produce valid JSON after retry: {cleaned_retry[:300]}") from error


def call_llm_for_text(system_prompt: str, user_prompt: str, temperature: float = 0.6) -> str:
    llm = get_llm(temperature=temperature)
    messages = [("system", system_prompt), ("human", user_prompt)]
    response = llm.invoke(messages)
    return response.content.strip()
