from fastapi import APIRouter, HTTPException, Query
from app.services.earnings_service import EarningsService

router = APIRouter()

@router.get("/earnings/{symbol}/earnings")
async def get_earnings(symbol: str):
    """Get annual earnings (Net Income)"""
    earnings_service = EarningsService()
    result = await earnings_service.get_earnings(symbol)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/earnings/{symbol}/quarterly_earnings")
async def get_quarterly_earnings(symbol: str):
    """Get quarterly earnings (Net Income)"""
    earnings_service = EarningsService()
    result = await earnings_service.get_quarterly_earnings(symbol)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/earnings/{symbol}/earnings_dates")
async def get_earnings_dates(
    symbol: str,
    limit: int = Query(default=12, description="Number of earnings dates to return")
):
    """Get earnings dates (future and historical)"""
    earnings_service = EarningsService()
    result = await earnings_service.get_earnings_dates(symbol, limit)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/earnings/{symbol}/revenue_estimate")
async def get_revenue_estimate(symbol: str):
    """Get revenue estimates"""
    earnings_service = EarningsService()
    result = await earnings_service.get_revenue_estimate(symbol)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/earnings/{symbol}/eps_revisions")
async def get_eps_revisions(symbol: str):
    """Get EPS revisions"""
    earnings_service = EarningsService()
    result = await earnings_service.get_eps_revisions(symbol)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/earnings/{symbol}/growth_estimates")
async def get_growth_estimates(symbol: str):
    """Get growth estimates"""
    earnings_service = EarningsService()
    result = await earnings_service.get_growth_estimates(symbol)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
