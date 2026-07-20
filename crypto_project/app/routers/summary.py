from fastapi import APIRouter, HTTPException
from app import schemas
from app.services import summary_service

router = APIRouter(prefix="/summary", tags=["summary"])

@router.post("/article", response_model=schemas.SummaryResponse)
async def summarize_article(request: schemas.SummaryRequest):
    """
    Summarize a single article by URL

- **url**: Article link
- **max_length**: Maximum summary length (default 200)
- **use_openai**: Use OpenAI for summarization (default False)
    """
    try:
        result = await summary_service.summarize_url(
            request.url,
            request.max_length,
            request.use_openai
        )
        return schemas.SummaryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))