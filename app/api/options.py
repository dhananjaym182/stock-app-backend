from fastapi import APIRouter, HTTPException, Query
from app.services.options_service import OptionsService
from typing import Optional

router = APIRouter()

@router.get("/options/{symbol}/options")
async def get_options_expiration_dates(symbol: str):
    """Get available options expiration dates"""
    options_service = OptionsService()
    result = await options_service.get_options_expiration_dates(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/options/{symbol}/option_chain")
async def get_option_chain(
    symbol: str,
    date: Optional[str] = Query(None, description="Option expiration date (YYYY-MM-DD format)")
):
    """Get option chain for specific expiration date"""
    options_service = OptionsService()
    result = await options_service.get_option_chain(symbol, date)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/options/{symbol}/calls")
async def get_calls_only(
    symbol: str,
    date: Optional[str] = Query(None, description="Option expiration date (YYYY-MM-DD format)")
):
    """Get only call options for specific expiration date"""
    options_service = OptionsService()
    result = await options_service.get_calls_only(symbol, date)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/options/{symbol}/puts")
async def get_puts_only(
    symbol: str,
    date: Optional[str] = Query(None, description="Option expiration date (YYYY-MM-DD format)")
):
    """Get only put options for specific expiration date"""
    options_service = OptionsService()
    result = await options_service.get_puts_only(symbol, date)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result
