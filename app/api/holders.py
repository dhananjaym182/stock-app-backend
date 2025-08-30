from fastapi import APIRouter, HTTPException
from app.services.holders_service import HoldersService

router = APIRouter()

@router.get("/holders/{symbol}/major_holders")
async def get_major_holders(symbol: str):
    """Get major holders"""
    holders_service = HoldersService()
    result = await holders_service.get_major_holders(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/holders/{symbol}/institutional_holders")
async def get_institutional_holders(symbol: str):
    """Get institutional holders"""
    holders_service = HoldersService()
    result = await holders_service.get_institutional_holders(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/holders/{symbol}/mutualfund_holders")
async def get_mutualfund_holders(symbol: str):
    """Get mutual fund holders"""
    holders_service = HoldersService()
    result = await holders_service.get_mutualfund_holders(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/holders/{symbol}/insider_purchases")
async def get_insider_purchases(symbol: str):
    """Get insider purchases"""
    holders_service = HoldersService()
    result = await holders_service.get_insider_purchases(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/holders/{symbol}/insider_transactions")
async def get_insider_transactions(symbol: str):
    """Get insider transactions"""
    holders_service = HoldersService()
    result = await holders_service.get_insider_transactions(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result

@router.get("/holders/{symbol}/insider_roster_holders")
async def get_insider_roster_holders(symbol: str):
    """Get insider roster holders"""
    holders_service = HoldersService()
    result = await holders_service.get_insider_roster_holders(symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"] else 500, detail=result["error"])
    
    return result
