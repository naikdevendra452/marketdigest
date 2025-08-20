import feedparser, httpx
from datetime import datetime, timedelta, timezone
from .summarizer import naive_summarize
from .firebase import get_db

# Example sources (use official feeds where possible)
FEEDS = [
    # Reuters India / Markets (use their topic feeds)
    "https://www.reuters.com/markets/asia/rss",  # example region feed
    # NSE RSS page has multiple endpoints — pick relevant once you explore:
    # https://www.nseindia.com/rss-feed  (index page listing feeds) :contentReference[oaicite:0]{index=0}
    # Add any Moneycontrol/ETMarkets RSS if available & permitted.
]

IST = timezone(timedelta(hours=5, minutes=30))

def _within_window(published: datetime) -> bool:
    # Window: 15:15 previous day → 08:15 today (IST)
    now_ist = datetime.now(IST)
    today_815 = now_ist.replace(hour=8, minute=15, second=0, microsecond=0)
    if now_ist < today_815:
        # we are before 08:15 -> window started yesterday 15:15
        start = (today_815 - timedelta(days=1)).replace(hour=15, minute=15)
        end = today_815
    else:
        # we are after 08:15 -> consider upcoming evening run window?
        start = now_ist.replace(hour=15, minute=15)
        end = (now_ist + timedelta(days=1)).replace(hour=8, minute=15)
    return start <= published <= end

def fetch_and_store():
    db = get_db()
    news_col = db.collection("news")
    seen = set()

    for url in FEEDS:
        d = feedparser.parse(url)
        for e in d.entries:
            title = e.get("title", "").strip()
            link = e.get("link", "").strip()
            if not title or not link or link in seen:
                continue
            # parse published time
            published = None
            if "published_parsed" in e and e.published_parsed:
                published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc).astimezone(IST)
            else:
                published = datetime.now(IST)
            if not _within_window(published):
                continue

            seen.add(link)
            raw = (e.get("summary") or e.get("description") or title).strip()
            summary = naive_summarize(raw, 3)
            doc_id = link.replace("/", "_")[:1500]
            news_col.document(doc_id).set({
                "source": url,
                "title": title,
                "link": link,
                "published_at": published.isoformat(),
                "summary": summary,
                "impact": "neutral",
                "sectors": [],
                "created_at": datetime.now(IST).isoformat()
            }, merge=True)

def build_digest():
    db = get_db()
    now_ist = datetime.now(IST)
    # Collect last window’s items
    start = (now_ist - timedelta(hours=16))  # easy heuristic
    q = (db.collection("news")
         .where("created_at", ">=", start.isoformat())
         .order_by("created_at", direction=firestore.Query.DESCENDING)  # type: ignore
        )
    # Firestore requires composite indexes for some queries; if error,
    # just fetch recent N and filter in memory:
    items = []
    for doc in db.collection("news").order_by("created_at", direction=firestore.Query.DESCENDING).limit(60).stream():  # type: ignore
        data = doc.to_dict()
        items.append(data)

    digest = {
        "when": now_ist.isoformat(),
        "items": items[:20]
    }
    db.collection("digests").add(digest)
    return digest
