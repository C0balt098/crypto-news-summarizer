from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routers import news, summary, digest  
from app.database import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crypto News Summarizer API",
    description="""
    # Crypto News Summarizer API
    
    API for collecting, processing, and summarizing cryptocurrency news.
    
    ## API Features:
    
    * News - collect and filter crypto news
    * Summarization - automatic creation of brief summaries
    * Digest - daily report with top stories
    * Categorization - automatic category detection
    * Cryptocurrencies - identify mentioned cryptocurrencies
    
    ## How to use:
    
    1. Get an API key from NewsAPI (https://newsapi.org/)
    2. Add the key to your .env file
    3. Start the server and use the endpoints below
    """,
    version="2.0.0",
    contact={
        "name": "API Support",
        "email": "support@crypto-news-api.com",
        "url": "https://github.com/yourusername/crypto-news-summarizer",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "news",
            "description": "News operations - fetching, filtering, and saving"
        },
        {
            "name": "summary",
            "description": "Article summarization - creating brief summaries and TL;DR"
        },
        {
            "name": "digest",
            "description": "Daily digests - statistics and top stories"
        }
    ]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(news.router)
app.include_router(summary.router)
app.include_router(digest.router)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Crypto News Summarizer API",
        version="2.0.0",
        description="""
        # Crypto News Summarizer API
        
        ## Overview
        
        API for automatic collection and summarization of cryptocurrency news.
        
        ### Key Features:
        
        - News Collection from NewsAPI by cryptocurrency
        - Automatic Summarization of articles with key points extraction
        - Categorization of news by topics (Markets, Technology, Regulation, etc.)
        - Cryptocurrency Detection in news text
        - Daily Digest with top 5 stories and statistics
        
        ### Getting Started:
        
        1. Get an API key from NewsAPI (https://newsapi.org/)
        2. Add NEWS_API_KEY=your_key to your .env file
        3. Start the server: uvicorn app.main:app --reload
        4. Use the endpoints below
        
        ### Example Requests:
        
        Get Bitcoin news:
        GET /news/fetch?currencies=Bitcoin&page_size=5
        
        Summarize an article:
        POST /summary/article
        {
          "url": "https://example.com/news",
          "max_length": 200
        }
        
        Get daily digest:
        GET /digest/daily
        
        ### Pro Tips:
        
        - Use days_back=1 for the most recent news
        - Filter by categories for relevant results
        - Background processing allows async summarization
        
        ## API Endpoints
        
        ### News Operations
        - GET /news/fetch - Fetch latest crypto news
        - GET /news/ - List saved news with filters
        - GET /news/recent - Get recent news by hours
        - GET /news/categories - List available categories
        - GET /news/cryptos - List cryptocurrencies in news
        
        ### Summarization
        - POST /summary/article - Summarize article by URL
        
        ### Daily Digest
        - GET /digest/daily - Get daily news digest
        """,
        routes=app.routes,
        tags=[
            {"name": "news", "description": "News management"},
            {"name": "summary", "description": "Article summarization"},
            {"name": "digest", "description": "Daily digests"}
        ]
    )
    
    # Add example requests
    openapi_schema["components"]["examples"] = {
        "FetchNewsRequest": {
            "summary": "Example news fetch request",
            "value": {
                "currencies": "Bitcoin,Ethereum,Solana",
                "page_size": 5,
                "days_back": 1,
                "use_openai": False
            }
        },
        "SummaryRequest": {
            "summary": "Example summarization request",
            "value": {
                "url": "https://cointelegraph.com/news/bitcoin-price-analysis",
                "max_length": 200,
                "use_openai": False
            }
        }
    }
    
    # Add response examples
    openapi_schema["components"]["responses"] = {
        "ValidationError": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "url"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        "NotFound": {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "example": {"detail": "No news found for the last 24 hours"}
                }
            }
        },
        "ServerError": {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error fetching news"}
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
def root():
    """
    Root endpoint with API information
    
    Returns:
    - Server status
    - List of all available endpoints
    - Documentation links
    """
    return {
        "message": "Crypto News Summarizer API",
        "status": "running",
        "version": "2.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "news": {
                "fetch": {
                    "method": "GET",
                    "path": "/news/fetch",
                    "description": "Fetch latest crypto news"
                },
                "list": {
                    "method": "GET",
                    "path": "/news/",
                    "description": "List saved news with filters"
                },
                "recent": {
                    "method": "GET",
                    "path": "/news/recent",
                    "description": "Get news from last N hours"
                },
                "categories": {
                    "method": "GET",
                    "path": "/news/categories",
                    "description": "List all news categories"
                },
                "cryptos": {
                    "method": "GET",
                    "path": "/news/cryptos",
                    "description": "List all cryptocurrencies"
                }
            },
            "summary": {
                "article": {
                    "method": "POST",
                    "path": "/summary/article",
                    "description": "Summarize article by URL"
                }
            },
            "digest": {
                "daily": {
                    "method": "GET",
                    "path": "/digest/daily",
                    "description": "Get daily news digest"
                }
            }
        }
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for service monitoring
    
    Used for monitoring API availability and status
    """
    import time
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)