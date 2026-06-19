# Gifty — Hyper-Personalised Gift Recommendation Agent

Gifty is an AI-powered backend that takes LinkedIn-style contact data and recommends the top 3 real, purchasable gifts for each contact. It is built as a multi-step LangGraph workflow, exposed through a FastAPI backend.

---

## What This Project Does

You give Gifty a contact's LinkedIn profile — their posts, comments, topics they engage with, their role, and their gift budget. Gifty then:

1. Reads the profile and extracts gifting signals (what this person genuinely seems to enjoy)
2. Filters out any sensitive signals (religion, health, politics, etc.)
3. Generates real Google Shopping search queries based on those signals
4. Searches for actual purchasable products using Serper (or DuckDuckGo as fallback)
5. Validates each product against budget, relevance, and professional appropriateness
6. Uses an LLM to rank the best 3 products and explain the reasoning
7. Writes a personalised gift note in the tone you specified
8. Stores the result and waits for a human to approve, reject, edit, or regenerate

---

## Folder Structure

```
gifty/
├── app/
│   ├── main.py               ← FastAPI routes (the HTTP layer)
│   ├── models.py             ← All data shapes (Pydantic models)
│   ├── llm_client.py         ← Wrapper to call the Groq LLM
│   ├── db.py                 ← SQLite storage using SQLModel
│   └── pipeline/
│       ├── extract_signals.py  ← Step 1: Read profile, extract gifting signals
│       ├── guardrails.py       ← Step 2: Remove sensitive signals
│       ├── search.py           ← Step 3 & 4: Generate queries + search products
│       ├── validate.py         ← Step 5: Check budget, relevance, appropriateness
│       ├── rank.py             ← Step 6: LLM picks and ranks top 3
│       ├── message_gen.py      ← Step 7: Write personalised gift note
│       └── orchestrator.py     ← LangGraph wires all steps into a workflow
├── requirements.txt
├── .env.example
└── sample_input.json
```

---

## Setup Instructions

### Step 1: Get your API keys

**Groq (required — it runs the LLM):**
- Go to https://console.groq.com/keys
- Create a free account and generate an API key
- Groq is free to use and very fast

**Serper (optional but recommended — finds real product links):**
- Go to https://serper.dev
- Create a free account (comes with 2,500 free searches)
- Without this key, Gifty falls back to DuckDuckGo (which works but finds fewer products)

### Step 2: Copy the environment file

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
GROQ_API_KEY=gsk_your_actual_groq_key
SERPER_API_KEY=your_actual_serper_key
```

### Step 3: Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Start the server

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`. The SQLite database (`gifty.db`) is created automatically on first run.

---

## How to Use the API

### Run the pipeline for one or more contacts

```bash
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d @sample_input.json
```

You can also pass multiple contacts in the `contacts` array — the pipeline runs for each one.

### List all processed contacts

```bash
curl http://localhost:8000/api/contacts
```

### Get one contact's full result

```bash
curl "http://localhost:8000/api/contacts/Aarav%20Mehta"
```

### Approve a recommendation

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"contact_name": "Aarav Mehta", "action": "approve"}'
```

### Reject a recommendation

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"contact_name": "Aarav Mehta", "action": "reject", "reviewer_note": "Too generic"}'
```

### Edit a specific gift (replace rank 1 with your own)

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "contact_name": "Aarav Mehta",
    "action": "edit",
    "edited_gift": {
      "rank": 1,
      "gift_name": "My Preferred Gift",
      "product_url": "https://amazon.in/some-product",
      "store": "Amazon",
      "estimated_price": "₹3,500",
      "why_this_gift": "Matches his cricket interest",
      "personalisation_reasoning": "From his recent posts",
      "personalised_message": "Hope you enjoy this!",
      "confidence_score": 0.9,
      "risk_level": "low",
      "assumptions": []
    }
  }'
```

### Regenerate recommendations from scratch

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"contact_name": "Aarav Mehta", "action": "regenerate"}'
```

### Check health (confirms keys are configured)

```bash
curl http://localhost:8000/api/health
```

---

## How the Workflow Works (Step by Step)

The entire pipeline is a **LangGraph StateGraph**. Think of it as a chain of steps where each step reads from a shared state, does its job, and passes the updated state to the next step.

Here is the order:

```
extract_signals → apply_guardrails → generate_queries → search_products
                → validate_products → rank_gifts → generate_messages → END
```

### Step 1: extract_signals (`extract_signals.py`)

The LLM reads the contact's LinkedIn profile — their headline, about section, work experience, recent posts, recent comments, and topics they engage with. It extracts three lists:

- **strong_signals**: Clear, specific interests (e.g. "enjoys cricket", "passionate about SaaS GTM")
- **weak_signals**: Indirect, lower-confidence inferences (e.g. "may enjoy leadership books based on role")
- **signals_to_avoid**: Anything sensitive that was spotted but must not be used

### Step 2: apply_guardrails (`guardrails.py`)

This step runs entirely without an LLM. It uses regex patterns to scan every signal for sensitive categories: religion, politics, health conditions, ethnicity, gender identity, family status. Any signal that matches gets removed and logged in the `guardrail_report`. This is a hard filter, not an opinion.

The same check is also applied to the LLM-generated search queries before they are sent to the search provider.

### Step 3 & 4: generate_queries + search_products (`search.py`)

The LLM generates 2-3 short Google Shopping-style queries based on the clean signals and the gift budget. For example: "cricket gift for business professional India under 5000".

These queries are sent to Serper's Shopping API to get real, purchasable product results. If Shopping returns nothing, it falls back to Serper's regular web search. If that also returns nothing, it falls back to DuckDuckGo. Product URLs are always from the search provider — the LLM cannot invent them.

### Step 5: validate_products (`validate.py`)

Each product returned by the search is checked against four rules:

1. Is the URL from a real purchasable store (not Wikipedia, Reddit, YouTube, etc.)?
2. Does the product title contain inappropriate keywords for professional gifting?
3. Is the price within 120% of the stated budget maximum?
4. Does the product title have at least some relevance to the contact's signals (checked by word overlap)?

Products that fail any check get a `rejection_reason` and are excluded from ranking.

### Step 6: rank_gifts (`rank.py`)

The LLM receives the full numbered list of validated products and the contact's signals. It picks up to 3 products and for each one explains:

- Why this gift fits the contact
- Which specific signal drove the pick
- A confidence score (0.0–1.0)
- Risk level (low / medium / high)
- Any assumptions it made that weren't directly stated

Crucially, the LLM can only pick from the provided product list. It cannot invent a new product URL. If the LLM step fails, the system falls back to relevance-score ordering with a clearly marked low confidence.

### Step 7: generate_messages (`message_gen.py`)

The LLM writes a short personalised note to accompany each of the 3 gifts. The tone is controlled by the `tone` field in `gift_context` — choose from `warm`, `formal`, `playful`, or `concise`. If the LLM fails, a safe generic fallback message is used.

---

## Human Review

After the pipeline runs, every contact result has `human_review.status = "pending_review"`. A human can then take one of four actions via the `/api/review` endpoint:

- **approve**: Mark the recommendations as accepted
- **reject**: Mark them as rejected (with an optional note)
- **edit**: Replace a specific gift with your own version (keeps everything else)
- **regenerate**: Rerun the entire pipeline from scratch for that contact

Every review action is logged in a `ReviewLog` table in SQLite, so there is a full audit trail of who changed what and when.

---

## Supported Tone Options

When submitting a contact, you can set `gift_context.tone` to one of:

- `warm` — Friendly and genuine, like a thoughtful colleague (default)
- `formal` — Polished and professional for senior executive relationships
- `playful` — Light and fun while still staying appropriate for business
- `concise` — 1-2 sentences, no extra words

---

## Error Handling and Fallbacks

- If the LLM fails to return valid JSON, it retries once with a correction prompt
- If signal extraction fails completely, weak signals fall back to the contact's role title
- If Serper Shopping returns nothing, it automatically tries Serper web search
- If Serper web search also returns nothing, it tries DuckDuckGo
- If a single contact fails entirely in a bulk run, that contact gets a degraded result with a clear warning — the rest of the batch still completes
- If the LLM ranking step fails, gifts are sorted by relevance score with a visible fallback note

---

## Evaluation Notes

Here is how quality would be measured in a real production setting:

**Gift relevance to profile**: Check if at least one strong signal from the profile appears in the gift's `personalisation_reasoning`. A human reviewer can rate 1-5.

**Valid product URLs**: Automated check — HTTP GET the product URLs and verify they return 200 status and look like a real product page (not 404, not a homepage).

**Budget fit**: Deterministic check — parse the `estimated_price` and verify it falls within `budget_min` and `budget_max`.

**Professional appropriateness**: Use a separate LLM call with a short rubric to rate whether the gift is suitable for the stated `relationship_type` (prospective customer vs. long-term partner, etc.).

**Sensitive signal avoidance**: Check the `guardrail_report` on every result. Also scan `why_this_gift` and `personalised_message` for any sensitive terms from the blocked categories.

**Personalised message quality**: Human rating, or an LLM evaluator that checks if the message references the occasion, avoids being generic, and stays appropriate in tone.

**Failure handling**: Run the pipeline with deliberately bad inputs (empty profile, no budget, nonsense signals) and verify that the warnings list is populated, confidence scores are low, and the result doesn't crash.

---

## Tradeoffs and What Could Be Improved

**Full results stored as JSON blobs in SQLite**: This is simple and works well for a prototype. For production, gifts would have their own table so you can query them independently.

**No streaming**: The pipeline runs synchronously. For a UI this would be slow on large batches. Adding async support and streaming intermediate steps back to the frontend would be the next step.

**DuckDuckGo fallback is fragile**: The HTML scraping approach can break if DuckDuckGo changes their page structure. For production, a dedicated product search API would be more reliable.

**Relevance scoring is keyword-based**: The `calculate_relevance_score` function does word overlap matching between signals and product titles. A semantic similarity model (embeddings) would give much better signal-to-product matching.

**Single LLM provider**: Everything runs through Groq. Adding an OpenAI or Anthropic fallback would make the system more resilient to provider outages.
