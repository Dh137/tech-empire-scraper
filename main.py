import os, datetime, json, random
from fastapi import FastAPI
from typing import List

app = FastAPI(title="Tech-Empire Scraper", version="1.0.0")
PORT = int(os.getenv("PORT", 8080))

# fake seed data (mimics Atlas structure)
MOCK_ARTICLES = [
    {
        "id": "1",
        "slug": "iphone-17-pro-leak-solid-state-buttons",
        "title": "iPhone 17 Pro Leak: Solid-State Buttons Are Back",
        "excerpt": "Supply-chain report says Apple solved yield issues for haptic volume keys.",
        "cover": "https://images.unsplash.com/photo-1603921327125-6e2b4f7a4be5?auto=format&fit=crop&w=1200&q=80",
        "source": "9to5Mac",
        "publishedAt": "2025-11-29T20:00:00Z",
        "aiSummary": "Apple will revert to solid-state buttons on iPhone 17 Pro after yield problems in ’25.",
        "whyItMatters": "Fewer moving parts = better durability + bigger battery space.",
        "counterPerspective": "Solid-state buttons still lack tactile feedback loved by power users.",
        "tags": ["mobile", "apple"],
        "createdAt": "2025-11-29T20:00:00Z"
    },
    {
        "id": "2",
        "slug": "google-gemini-15-beats-gpt4o-code",
        "title": "Google’s Gemini 1.5 Beats GPT-4o on Code Generation",
        "excerpt": "New 2M context model scores 84 % on HumanEval, up from 74 %.",
        "cover": "https://images.unsplash.com/photo-1677442135722-5f8ea49cec8a?auto=format&fit=crop&w=1200&q=80",
        "source": "Ars Technica",
        "publishedAt": "2025-11-29T18:00:00Z",
        "aiSummary": "Gemini 1.5 uses longer context window to outperform GPT-4o on coding benchmarks.",
        "whyItMatters": "Cheaper, faster code assistance for indie hackers.",
        "counterPerspective": "Benchmarks ≠ real-world IDE latency; GPT-4o still wins on UX polish.",
        "tags": ["ai", "dev"],
        "createdAt": "2025-11-29T18:00:00Z"
    }
]

@app.post("/scrape")
def scrape():
    # simulate a scrape: just shuffle timestamps
    for a in MOCK_ARTICLES:
        a["createdAt"] = datetime.datetime.utcnow().isoformat()
    return {"inserted": len(MOCK_ARTICLES)}

@app.get("/articles")
def list_articles(limit: int = 20):
    return MOCK_ARTICLES[:limit]

@app.get("/health")
def health():
    return {"status": "ok"}