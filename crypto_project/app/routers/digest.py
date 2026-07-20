from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/digest", tags=["digest"])

@router.get("/daily", response_model=schemas.DailyDigestResponse)
def get_daily_digest(db: Session = Depends(get_db)):
    """
    Get daily news digest
    
    Returns:
    - Statistics by category
    - Top 5 news stories
    - Summary digest text
    """
    digest_data = crud.get_daily_digest(db)
    
    if not digest_data:
        raise HTTPException(status_code=404, detail="No news found for the last 24 hours")
    
    # Generate digest text
    digest_text = generate_digest_text(digest_data)
    
    # Save digest to database
    digest = crud.create_daily_digest(db, digest_data)
    
    return schemas.DailyDigestResponse(
        date=datetime.utcnow(),
        articles_count=len(digest_data["articles"]),
        categories=digest_data["categories"],
        top_stories=[{
            "id": a.id,
            "title": a.title,
            "summary": a.summary or "No summary available",
            "category": a.category or "General"
        } for a in digest_data["top_stories"]],
        digest_text=digest_text
    )

def generate_digest_text(digest_data: dict) -> str:
    """Generate digest text"""
    articles = digest_data["articles"]
    categories = digest_data["categories"]
    crypto_stats = digest_data.get("crypto_stats", {})
    
    digest = f"**Daily Crypto News Digest**\n"
    digest += f"{datetime.utcnow().strftime('%d.%m.%Y')}\n\n"
    
    # Statistics
    digest += f"**Statistics:**\n"
    digest += f"Total news: {len(articles)}\n"
    for category, count in categories.items():
        digest += f"{category}: {count}\n"
    
    if crypto_stats:
        digest += f"\n**Cryptocurrencies:**\n"
        for crypto, count in sorted(crypto_stats.items(), key=lambda x: x[1], reverse=True)[:3]:
            digest += f"{crypto}: {count}\n"
    
    # Top stories
    digest += f"\n**Top 5 Stories of the Day:**\n\n"
    for i, article in enumerate(digest_data["top_stories"][:5], 1):
        digest += f"{i}. **{article.title}**\n"
        if article.summary:
            digest += f"   {article.summary}\n"
        if article.key_takeaways:
            for takeaway in article.key_takeaways[:2]:
                digest += f"   - {takeaway}\n"
        digest += f"   Category: {article.category or 'General'}\n"
        digest += f"   Link: {article.url}\n\n"
    
    digest += f"\n**TL;DR:** {crypto_stats}\n"
    digest += f"More news: /news/"
    
    return digest