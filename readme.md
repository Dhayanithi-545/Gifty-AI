# Gifty AI

Gifty is an AI-powered gift recommendation system that helps you figure out what gift to send to a professional contact without relying on random guesses.

Imagine you've just met a potential customer, a business partner, an investor, or someone you've been building a relationship with on LinkedIn. You know a little about them from their profile, posts, and interests, but choosing a thoughtful gift still takes time.

That's where Gifty comes in.

You give Gifty information about a contact and a budget. It studies their profile, understands what they seem to care about, finds real products that can actually be purchased online, ranks the best options, and even writes a personalized gift message.

The goal is simple.

Help people send better gifts that feel personal, professional, and relevant.

## What Gifty Does

When you provide a contact profile, Gifty will:

* Read the profile and identify meaningful interests
* Remove sensitive information that should never influence gifting decisions
* Generate intelligent shopping queries
* Search for real products from the web
* Validate products against budget and appropriateness rules
* Rank the best gift options
* Generate personalized gift notes
* Keep everything ready for human review before approval

The entire workflow runs through a multi-step AI pipeline built using LangGraph and FastAPI.

## Tech Stack

**Backend**

* Python
* FastAPI
* LangGraph
* Pydantic
* SQLite
* Groq
* Serper

**Frontend**

* React
* Vite
* Tailwind CSS

## Getting Started

After cloning the repository, follow the steps below.

### Backend Setup

Open a terminal and run:

```bash
git clone https://github.com/Dhayanithi-545/Gifty-AI.git

cd Gifty-AI/backend

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

Open the `.env` file and add your API keys.

```env
GROQ_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
```

Now start the backend:

```bash
uvicorn app.main:app --reload
```

The API should now be running at:

```text
http://localhost:8000
```

### Frontend Setup

Open another terminal and run:

```bash
cd Gifty-AI/frontend

npm install

npm run dev
```

The frontend should now be available at:

```text
http://localhost:5173
```

## Project Structure

```text
Gifty-AI/

├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

## How It Works

The workflow is intentionally broken into multiple stages so that every step is easy to understand and improve.

```text
Profile Input

↓

Signal Extraction

↓

Safety Guardrails

↓

Query Generation

↓

Product Search

↓

Product Validation

↓

Gift Ranking

↓

Message Generation

↓

Human Review
```

Each stage has a single responsibility and passes its output to the next stage.

This makes the system easier to debug, extend, and scale in the future.

## Why I Built This

Most gift recommendations on the internet are generic.

People search for things like:

> gifts for managers

> gifts for founders

> gifts for clients

The results are usually the same list repeated everywhere.

I wanted to build something that actually looks at the individual person and recommends gifts based on signals from their professional profile.

Gifty is my attempt at solving that problem using AI agents, workflow orchestration, search systems, and real-world product validation.

## Future Improvements

Some things I'd like to add next:

* Better semantic matching using embeddings
* Multiple LLM provider support
* Product recommendation feedback loops
* Async workflow execution
* Live progress updates in the UI
* Advanced evaluation dashboards
* More e-commerce integrations

## Running Into Issues?

If something breaks:

1. Make sure your virtual environment is activated
2. Check that your API keys are present in `.env`
3. Verify all dependencies were installed correctly
4. Restart both frontend and backend servers
5. Check the terminal logs first before assuming the AI is the problem

Most setup issues usually come from missing environment variables or dependency installation problems.

## Final Note

This project was built as a practical AI workflow that combines profile understanding, search, validation, ranking, and personalization into a single system.

If you're exploring LangGraph, FastAPI, agent workflows, or AI-powered recommendation systems, feel free to fork it, break it, improve it, and make it your own.
