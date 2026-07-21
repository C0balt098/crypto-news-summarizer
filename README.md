#Crypto News Summarizer API
##Description
Crypto News Summarizer API is a web service built with FastAPI for collecting, processing, and summarizing cryptocurrency news. The service automatically retrieves news through NewsAPI, analyzes content, determines categories, and creates brief digests.

##Features
News Collection - automatic collection of crypto news through NewsAPI

Intelligent Summarization - creating concise and informative news summaries

Categorization - automatic detection of news categories (Markets, Technology, Regulation, Security, Adoption)

Cryptocurrency Detection - identifying the main cryptocurrency mentioned in the news

Daily Digest - generating a summary report with top stories

Background Processing - asynchronous article processing without response delay

Swagger Documentation - interactive API documentation

##Technology Stack
FastAPI - modern web framework

SQLAlchemy - ORM for database operations

SQLite / PostgreSQL - database management systems

NewsAPI - external API for news retrieval

BeautifulSoup4 - HTML parsing

Pydantic - data validation

Uvicorn - ASGI server

##Installation and Setup
1. Clone Repository
git clone [https://github.com/yourusername/crypto-news-summarizer.git](https://github.com/C0balt098/crypto-news-summarizer.git)
cd crypto-news-summarizer
2. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate     # For Windows
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables
# Database (SQLite by default)
DATABASE_URL=sqlite:///./crypto_news.db

## NewsAPI key (get at https://newsapi.org/)
NEWS_API_KEY=your_newsapi_key_here

## OpenAI key (optional, for advanced summarization)
OPENAI_API_KEY=your_openai_key_here
5. Run Application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
The application will be available at: http://localhost:8000
API Documentation
After starting the application, documentation is available at:

##Swagger UI: http://localhost:8000/docs

##ReDoc: http://localhost:8000/redoc

###Security
All API keys are stored in .env file and not exposed in code

CORS settings are configured for access control
