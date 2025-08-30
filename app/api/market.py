from fastapi import APIRouter, HTTPException, Query
from app.services.market_service import MarketService, AVAILABLE_MARKETS
from typing import Optional

router = APIRouter()

@router.get("/market/{market_name}/status")
async def get_market_status(market_name: str):
    """Get market status"""
    if market_name.upper() not in AVAILABLE_MARKETS:
        raise HTTPException(status_code=404, detail='Invalid market name')
    
    market_service = MarketService()
    status = await market_service.get_market_status(market_name)
    
    if status is None:
        raise HTTPException(status_code=500, detail='Failed to fetch market status')
    
    return status

@router.get("/market/{market_name}/summary")
async def get_market_summary(market_name: str):
    """Get market summary"""
    if market_name.upper() not in AVAILABLE_MARKETS:
        raise HTTPException(status_code=404, detail='Invalid market name')
    
    market_service = MarketService()
    summary = await market_service.get_market_summary(market_name)
    
    if summary is None:
        raise HTTPException(status_code=500, detail='Failed to fetch market summary')
    
    return summary

@router.get("/market/available_markets")
async def get_available_markets():
    """Get list of available markets"""
    market_service = MarketService()
    return market_service.get_available_markets()

@router.get("/market/bulk_download")
async def bulk_download(
    tickers: str = Query(..., description="Comma or space separated ticker symbols"),
    period: str = Query(default="1mo", description="Data period"),
    interval: str = Query(default="1d", description="Data interval")
):
    """Download data for multiple tickers at once"""
    if not tickers.strip():
        raise HTTPException(status_code=400, detail='Tickers parameter required')
    
    market_service = MarketService()
    result = await market_service.bulk_download(tickers, period, interval)
    
    if result is None:
        raise HTTPException(status_code=500, detail='Bulk download failed')
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
