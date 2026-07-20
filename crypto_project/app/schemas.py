from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NewsArticleBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    published_at: datetime
    category: Optional[str] = None
    crypto: Optional[str] = None  

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticleResponse(NewsArticleBase):
    id: int
    summary: Optional[str] = None
    key_takeaways: Optional[List[str]] = None
    tldr: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SummaryRequest(BaseModel):
    url: str
    max_length: Optional[int] = 200
    use_openai: Optional[bool] = False

class SummaryResponse(BaseModel):
    url: str
    summary: str
    key_takeaways: List[str]
    category: str
    tldr: str

class DailyDigestResponse(BaseModel):
    date: datetime
    articles_count: int
    categories: dict
    top_stories: List[dict]
    digest_text: str

class FetchNewsRequest(BaseModel):
    currencies: Optional[List[str]] = None
    page_size: Optional[int] = 20
    days_back: Optional[int] = 1
    use_openai: Optional[bool] = False