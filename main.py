import os, feedparser, datetime, logging, json
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()
app = FastAPI(title="Tech-Empire Scraper", version="1.0.0")
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database("tech-empire")
articles = db.articles
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PORT = int(os.getenv("PORT", 8080))

SOURCES = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "9to5Mac": "https://9to5mac.com/feed/",
}

def summarize(text: str) -> dict:
    prompt = f"""
You are a snarky, concise tech-news writer.
Rewrite the article below into:
- title (max 12 words)
- excerpt (1 sentence)
- aiSummary (1 sentence)
- whyItMatters (1 sentence)
- counterPerspective (1 sentence)
- tags (2 lowercase words: tech-field + company/product)

Return ONLY valid JSON with those keys.
Article:
{text}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250,
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        logging.exception("OpenAI error")
        return {}

@app.post("/scrape", response_model=dict)
def scrape():
    total = 0
    for source, url in SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            if articles.find_one({"slug": entry.id or entry.link}):
                continue
            try:
                body = entry.summary if hasattr(entry, "summary") else entry.title
                ai = summarize(body)
                if not ai:
                    continue
                doc = {
                    "id": entry.id or entry.link,
                    "slug": entry.link.split("/")[-2] or entry.id,
                    "title": ai["title"],
                    "excerpt": ai["excerpt"],
                    "cover": entry.get("media_content", [{}])[0].get("url", ""),
                    "source": source,
                    "publishedAt": datetime.datetime(*entry.published_parsed[:6]).isoformat(),
                    "aiSummary": ai["aiSummary"],
                    "whyItMatters": ai["whyItMatters"],
                    "counterPerspective": ai["counterPerspective"],
                    "tags": ai["tags"],
                    "createdAt": datetime.datetime.utcnow(),
                }
                articles.insert_one(doc)
                total += 1
            except Exception as e:
                logging.exception("parse error")
    return {"inserted": total}

@app.get("/articles", response_model=List[dict])
def list_articles(limit: int = 20):
    docs = list(articles.find({}, {"_id": 0}).sort("createdAt", -1).limit(limit))
    return docs

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)