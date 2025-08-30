from fastapi import APIRouter, HTTPException
from app.services.fund_service import FundService

router = APIRouter()

@router.get("/fund/{symbol}/funds_data")
async def get_funds_data(symbol: str):
    """Get comprehensive fund data (for ETFs/Mutual Funds)"""
    fund_service = FundService()
    result = await fund_service.get_funds_data(symbol)
    
    if "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/fund/{symbol}/top_holdings")
async def get_fund_top_holdings(symbol: str):
    """Get fund top holdings only"""
    fund_service = FundService()
    result = await fund_service.get_fund_top_holdings(symbol)
    
    if "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/fund/{symbol}/sector_weightings")
async def get_fund_sector_weightings(symbol: str):
    """Get fund sector weightings only"""
    fund_service = FundService()
    result = await fund_service.get_fund_sector_weightings(symbol)
    
    if "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
