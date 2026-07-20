from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

def create_article(db: Session, article: schemas.NewsArticleCreate):
    db_article = models.NewsArticle(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_articles(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    crypto: Optional[str] = None
):
    query = db.query(models.NewsArticle)
    if category:
        query = query.filter(models.NewsArticle.category == category)
    if crypto:
        query = query.filter(models.NewsArticle.crypto == crypto)
    return query.offset(skip).limit(limit).all()

def get_article_by_url(db: Session, url: str):
    return db.query(models.NewsArticle).filter(models.NewsArticle.url == url).first()

def get_recent_articles(db: Session, hours: int = 24):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return db.query(models.NewsArticle).filter(
        models.NewsArticle.published_at >= cutoff
    ).order_by(models.NewsArticle.published_at.desc()).all()

def save_summary(db: Session, article_id: int, summary: str, takeaways: list, category: str, tldr: str):
    article = db.query(models.NewsArticle).filter(models.NewsArticle.id == article_id).first()
    if article:
        article.summary = summary
        article.key_takeaways = takeaways
        article.category = category
        article.tldr = tldr
        db.commit()
        db.refresh(article)
    return article

# =============================================
# DIGEST FUNCTIONS
# =============================================

def get_daily_digest(db: Session) -> Dict[str, Any]:
    """Get data for daily digest"""
    articles = get_recent_articles(db, hours=24)
    
    if not articles:
        return None
    
    categories = {}
    crypto_stats = {}
    for article in articles:
        cat = article.category or "General"
        categories[cat] = categories.get(cat, 0) + 1
        
        crypto = article.crypto or "Cryptocurrency"
        crypto_stats[crypto] = crypto_stats.get(crypto, 0) + 1
    
    top_stories = sorted(
        articles,
        key=lambda x: (x.summary is not None, x.published_at),
        reverse=True
    )[:5]
    
    return {
        "articles": articles,
        "categories": categories,
        "crypto_stats": crypto_stats,
        "top_stories": top_stories
    }

def create_daily_digest(db: Session, digest_data: Dict[str, Any]):
    """Create daily digest record"""
    top_stories_data = []
    for article in digest_data["top_stories"]:
        top_stories_data.append({
            "id": article.id,
            "title": article.title,
            "summary": article.summary or "No summary available",
            "category": article.category or "General",
            "url": article.url
        })
    
    digest = models.DailyDigest(
        articles_count=len(digest_data["articles"]),
        categories=digest_data["categories"],
        top_stories=top_stories_data,
        digest_text=""
    )
    db.add(digest)
    db.commit()
    db.refresh(digest)
    return digest