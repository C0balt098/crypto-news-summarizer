import os
from typing import List, Tuple
import re

def summarize_article(text: str, max_length: int = 200, use_openai: bool = False) -> Tuple[str, List[str], str]:
    text = text.strip()
    
    if len(text) > max_length:
        summary = text[:max_length]
        last_space = summary.rfind(' ')
        last_dot = summary.rfind('.')
        cut_at = max(last_dot, last_space)
        if cut_at > 0:
            summary = summary[:cut_at + 1]
        summary = summary + "..."
    else:
        summary = text
    
    takeaways = []
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    
    for i, sentence in enumerate(sentences[:3]):
        if sentence:
            if len(sentence) > 80:
                sentence = sentence[:77] + "..."
            takeaways.append(f"✓ {sentence}")
    
    if not takeaways:
        takeaways = [
            "Important events in the crypto industry",
            "Impact on the cryptocurrency market",
            "Requires investor attention"
        ]
    
    category = detect_category(text)
    return summary, takeaways[:5], category

def detect_category(text: str) -> str:
    """Determining news category"""
    text_lower = text.lower()
    categories = {
        "Markets": ["price", "market", "trading", "investment", "fund", "etf", "inflow", "outflow"],
        "Technology": ["technology", "protocol", "upgrade", "developer", "code", "launch", "update"],
        "Regulation": ["regulation", "law", "legal", "government", "sec", "regulatory", "ban"],
        "Security": ["hack", "scam", "fraud", "security", "breach", "attack"],
        "Adoption": ["adopt", "accept", "use", "payment", "partnership", "integration"]
    }
    
    for category, keywords in categories.items():
        if any(word in text_lower for word in keywords):
            return category
    return "General"

async def summarize_url(url: str, max_length: int = 200, use_openai: bool = False) -> dict:
    """
    Summarizing an article by URL
    """
    try:
        import httpx
        from bs4 import BeautifulSoup
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            
            paragraphs = soup.find_all('p')
            text = ' '.join([p.text for p in paragraphs if len(p.text) > 50])
            
            if not text:
                text = ' '.join(soup.get_text().split())
            
            text = text[:5000]  
            
            if len(text) < 50:
                return {
                    "url": url,
                    "summary": "Unable to extract text from article",
                    "key_takeaways": ["Please check the URL or try another article."],
                    "category": "General",
                    "tldr": "Error extracting text"
                }
            
            summary, takeaways, category = summarize_article(text, max_length, use_openai)
            
            tldr = summary[:100] + "..." if len(summary) > 100 else summary
            
            return {
                "url": url,
                "summary": summary,
                "key_takeaways": takeaways,
                "category": category,
                "tldr": tldr
            }
            
    except Exception as e:
        return {
            "url": url,
            "summary": f"Error retrieving article: {str(e)}",
            "key_takeaways": ["Try another article"],
            "category": "General",
            "tldr": "Error"
        }