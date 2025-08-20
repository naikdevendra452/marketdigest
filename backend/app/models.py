from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime

class SignupIn(BaseModel):
    name: str = ""
    email: EmailStr
    password: str

class PrefsIn(BaseModel):
    email: bool = True
    whatsapp: bool = False
    morning: bool = True   # 8 AM
    evening: bool = True   # 9 PM

class NewsItem(BaseModel):
    id: str
    source: str
    title: str
    link: str
    published_at: datetime
    summary: str
    impact: Literal["positive","negative","neutral"] = "neutral"
    sectors: List[str] = []

class DigestOut(BaseModel):
    when: datetime
    items: List[NewsItem] = []
