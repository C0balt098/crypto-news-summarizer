from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class NewsArticle(Base):
    __tablename__ = "news_article"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False, unique=True)
    source = Column(String(100), nullable=False)
    published_at = Column(DateTime, nullable=False)
    category = Column(String(50), nullable=True)
    crypto = Column(String(50), nullable=True) 
    summary = Column(Text, nullable=True)
    key_takeaways = Column(JSON, nullable=True)
    tldr = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class DailyDigest(Base):
    __tablename__ = "daily_digests"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    articles_count = Column(Integer, default=0)
    digest_text = Column(Text, nullable=True)
    categories = Column(JSON, nullable=True)
    top_stories = Column(JSON, nullable=True)

