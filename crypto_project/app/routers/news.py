from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app import crud, schemas, models
from app.services import news_service, summary_service

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/fetch", response_model=List[schemas.NewsArticleResponse])
async def fetch_news(
    currencies: Optional[str] = Query(None, description="Cryptocurrencies separated by commas (Bitcoin, Ethereum, Solana)"),
    page_size: int = Query(5, description="Number of news items (max 20)"),
    days_back: int = Query(1, description="Number of days ago"),
    use_openai: bool = Query(False, description="Use OpenAI for summarization"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Receive cryptocurrency news

Example: /news/fetch?currencies=Bitcoin,Ethereum&page_size=5
    """
    try:
        currency_list = None
        if currencies:
            currency_list = [c.strip() for c in currencies.split(',') if c.strip()]
        
        articles = await news_service.fetch_crypto_news(
            currencies=currency_list,
            page_size=min(page_size, 20),  
            days_back=days_back
        )
        
        saved_articles = []
        for article in articles:
            existing = crud.get_article_by_url(db, article.url)
            if not existing:
                db_article = models.NewsArticle(
                    title=article.title,
                    description=article.description,
                    url=article.url,
                    source=article.source,
                    published_at=article.published_at,
                    category=article.category,
                    crypto=article.crypto
                )
                db.add(db_article)
                db.commit()
                db.refresh(db_article)
                saved_articles.append(db_article)
                
                if background_tasks:
                    background_tasks.add_task(
                        process_article,
                        db_article.id,
                        article.description or article.title,
                        use_openai
                    )
        
        return saved_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.NewsArticleResponse])
def get_news(
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Maximum number of entries"),
    category: Optional[str] = Query(None, description="Filter by category"),
    crypto: Optional[str] = Query(None, description="Filter by cryptocurrency"),
    db: Session = Depends(get_db)
):
    """Receive saved news with filtering"""
    articles = crud.get_articles(db, skip=skip, limit=limit, category=category, crypto=crypto)
    return articles

@router.get("/recent", response_model=List[schemas.NewsArticleResponse])
def get_recent_news(
    hours: int = Query(24, description="Number of hours ago"),
    db: Session = Depends(get_db)
):
    """Receive news for the last N hours"""
    articles = crud.get_recent_articles(db, hours=hours)
    return articles

@router.get("/categories", response_model=dict)
def get_categories(db: Session = Depends(get_db)):
    """Getting a list of categories"""
    categories = db.query(models.NewsArticle.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}

@router.get("/cryptos", response_model=dict)
def get_cryptos(db: Session = Depends(get_db)):
    """Getting a list of cryptocurrencies"""
    cryptos = db.query(models.NewsArticle.crypto).distinct().all()
    return {"cryptos": [c[0] for c in cryptos if c[0]]}

async def process_article(article_id: int, text: str, use_openai: bool):
    """Background task for article summarization"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        summary, takeaways, category = summary_service.summarize_article(text, 200, use_openai)
        tldr = summary[:100] + "..." if len(summary) > 100 else summary
        crud.save_summary(db, article_id, summary, takeaways, category, tldr)
    finally:
        db.close()