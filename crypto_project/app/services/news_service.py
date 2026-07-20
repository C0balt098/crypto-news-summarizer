import os
import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from app import schemas
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

CRYPTO_CURRENCIES = ["Bitcoin", "Ethereum", "Solana", "Cardano", "Ripple", "Dogecoin", "Polkadot"]

async def fetch_crypto_news(
    currencies: Optional[List[str]] = None,
    page_size: int = 20,
    days_back: int = 1
) -> List[schemas.NewsArticleCreate]:
    """
    Receive cryptocurrency news via NewsAPI
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "your_newsapi_key_here":
        raise Exception("NewsAPI key is missing. Please add NEWS_API_KEY to .env file")
    
    if currencies is None:
        currencies = CRYPTO_CURRENCIES
    
    query = " OR ".join(currencies)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
            "pageSize": page_size,
            "from": (datetime.utcnow().replace(hour=0, minute=0, second=0) - 
                    timedelta(days=days_back)).isoformat()
        }
        
        try:
            response = await client.get(NEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            
            articles = []
            for item in data.get("articles", []):
                if not item.get("title") or not item.get("url"):
                    continue
                
                if not item.get("description"):
                    continue
                
                category = detect_category(
                    f"{item.get('title', '')} {item.get('description', '')}"
                )
                
                crypto = detect_crypto(
                    f"{item.get('title', '')} {item.get('description', '')}"
                )
                
                try:
                    published_at = datetime.fromisoformat(
                        item.get("publishedAt", "").replace("Z", "+00:00")
                    )
                except:
                    published_at = datetime.utcnow()
                
                article = schemas.NewsArticleCreate(
                    title=item.get("title", "No title"),
                    description=item.get("description") or "No description available",
                    url=item.get("url"),
                    source=item.get("source", {}).get("name", "Unknown"),
                    published_at=published_at,
                    category=category,
                    crypto=crypto
                )
                articles.append(article)
            
            if not articles:
                raise Exception("No articles found for the specified criteria")
            
            return articles
            
        except httpx.TimeoutException:
            raise Exception("NewsAPI request timeout. Please try again later.")
        except httpx.HTTPStatusError as e:
            raise Exception(f"NewsAPI HTTP error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Error fetching news: {str(e)}")

def detect_category(text: str) -> str:
    """Determining news category"""
    text_lower = text.lower()
    categories = {
        "Regulation": ["regulation", "law", "legal", "government", "sec", "regulatory", "ban", "approve"],
        "Technology": ["technology", "protocol", "upgrade", "developer", "code", "launch", "update", "scaling"],
        "Markets": ["price", "market", "trading", "investment", "fund", "etf", "stock", "exchange"],
        "Security": ["hack", "scam", "fraud", "security", "breach", "vulnerability", "attack"],
        "Adoption": ["adopt", "accept", "use", "payment", "partnership", "integration"]
    }
    
    for category, keywords in categories.items():
        if any(word in text_lower for word in keywords):
            return category
    return "General"

def detect_crypto(text: str) -> str:
    """Definition of cryptocurrency in the news"""
    text_lower = text.lower()
    crypto_map = {
        "bitcoin": "Bitcoin",
        "btc": "Bitcoin",
        "ethereum": "Ethereum",
        "eth": "Ethereum",
        "solana": "Solana",
        "sol": "Solana",
        "cardano": "Cardano",
        "ada": "Cardano",
        "ripple": "Ripple",
        "xrp": "Ripple",
        "dogecoin": "Dogecoin",
        "doge": "Dogecoin",
        "polkadot": "Polkadot",
        "dot": "Polkadot"
    }
    
    for key, value in crypto_map.items():
        if key in text_lower:
            return value
    return "Cryptocurrency"