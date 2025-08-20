from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from .models import SignupIn, PrefsIn, DigestOut
from .deps import hash_pw, verify_pw
from .firebase import get_db
from .news_job import fetch_and_store, build_digest

app = FastAPI(title="MarketDigest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "now": datetime.utcnow().isoformat()}

@app.post("/auth/signup")
def signup(body: SignupIn):
    db = get_db()
    users = db.collection("users")
    if list(users.where("email","==",body.email).limit(1).stream()):
        raise HTTPException(400, "Email already exists")
    users.add({
        "name": body.name,
        "email": body.email,
        "password": hash_pw(body.password),
        "created_at": datetime.utcnow().isoformat(),
        "prefs": {"email": True, "whatsapp": False, "morning": True, "evening": True},
    })
    return {"ok": True}

@app.post("/auth/login")
def login(email: EmailStr, password: str):
    db = get_db()
    q = db.collection("users").where("email","==",email).limit(1).stream()
    user = next(q, None)
    if not user:
        raise HTTPException(400, "Invalid credentials")
    data = user.to_dict()
    if not verify_pw(password, data.get("password","")):
        raise HTTPException(400, "Invalid credentials")
    return {"ok": True}

@app.post("/prefs")
def save_prefs(email: EmailStr, prefs: PrefsIn):
    db = get_db()
    q = db.collection("users").where("email","==",email).limit(1).stream()
    snap = next(q, None)
    if not snap:
        raise HTTPException(404, "User not found")
    snap.reference.update({"prefs": prefs.dict()})
    return {"ok": True}

@app.get("/digests", response_model=List[DigestOut])
def digests():
    db = get_db()
    results = []
    for d in db.collection("digests").order_by("when", direction=firestore.Query.DESCENDING).limit(10).stream():  # type: ignore
        results.append(d.to_dict())
    return results

# Protected task endpoint (called by Cloud Scheduler with OIDC)
@app.post("/tasks/run-digest")
def run_digest(secret: str):
    # Simple protection first; replace with OIDC in Cloud Scheduler later
    from os import getenv
    if secret != getenv("CRON_SECRET","changeme"):
        raise HTTPException(401, "Unauthorized")
    fetch_and_store()
    digest = build_digest()
    # TODO: send email (SendGrid) and WhatsApp via Meta API if keys configured
    return {"ok": True, "count": len(digest["items"])}
