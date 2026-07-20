from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import news, summary, digest  
from app.database import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crypto News Summarizer API",
    description="Receiving and summarizing cryptocurrency news",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(summary.router)
app.include_router(digest.router)  

@app.get("/")
def root():
    return {
        "message": "Crypto News Summarizer API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "news": {
                "fetch": "POST /news/fetch - Get latest crypto news",
                "list": "GET /news/ - Get saved news",
                "recent": "GET /news/recent - Get recent news",
                "categories": "GET /news/categories - Get categories",
                "cryptos": "GET /news/cryptos - Get cryptocurrencies"
            },
            "summary": {
                "article": "POST /summary/article - Summarize single article"
            },
            "digest": {
                "daily": "GET /digest/daily - Get daily digest"
            },
            "docs": "GET /docs - API Documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)