from fastapi import APIRouter, HTTPException
from app.services.screening_service import ScreeningService
from typing import Dict, Any

router = APIRouter()

@router.post("/screener/equity_screen")
async def equity_screen(criteria: Dict[str, Any]):
    """Screen equities based on criteria"""
    screening_service = ScreeningService()
    result = await screening_service.equity_screen(criteria)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/screener/fund_screen")
async def fund_screen(criteria: Dict[str, Any]):
    """Screen funds based on criteria"""
    screening_service = ScreeningService()
    result = await screening_service.fund_screen(criteria)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/screener/predefined_screens")
async def get_predefined_screens():
    """Get list of predefined screening criteria"""
    screening_service = ScreeningService()
    return screening_service.get_predefined_screens()
