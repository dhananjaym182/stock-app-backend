from fastapi import APIRouter, HTTPException
from app.services.ai_analysis_service import AIAnalysisService

router = APIRouter()

@router.get("/ai-analysis/{symbol}")
async def get_ai_analysis(symbol: str):
    """Get AI-powered stock analysis - backward compatible with Flask API"""
    ai_service = AIAnalysisService()
    result = await ai_service.get_ai_analysis(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
