from fastapi import APIRouter, HTTPException
from app.services.yfinance_analysis_service import YfinanceAnalysisService

router = APIRouter()

@router.get("/yanalysis/{symbol}/analyst_price_targets")
async def get_analyst_price_targets(symbol: str):
    """Get analyst price targets"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_analyst_price_targets(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/yanalysis/{symbol}/recommendations")
async def get_recommendations(symbol: str):
    """Get analyst recommendations"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_recommendations(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/yanalysis/{symbol}/recommendations_summary")
async def get_recommendations_summary(symbol: str):
    """Get recommendations summary"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_recommendations_summary(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/yanalysis/{symbol}/upgrades_downgrades")
async def get_upgrades_downgrades(symbol: str):
    """Get upgrades and downgrades"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_upgrades_downgrades(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/yanalysis/{symbol}/earnings_estimates")
async def get_earnings_estimates(symbol: str):
    """Get earnings estimates"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_earnings_estimates(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/yanalysis/{symbol}/financial_estimates")
async def get_financial_estimates(symbol: str):
    """Get financial estimates"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_financial_estimates(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/yanalysis/{symbol}/sustainability")
async def get_sustainability(symbol: str):
    """Get sustainability data"""
    analysis_service = YfinanceAnalysisService()
    result = await analysis_service.get_sustainability(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result
