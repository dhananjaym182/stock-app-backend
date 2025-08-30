from fastapi import APIRouter, HTTPException
from app.services.sector_service import SectorService

router = APIRouter()

@router.get("/sector/{sector_key}")
async def get_sector_info(sector_key: str):
    """Get sector information"""
    sector_service = SectorService()
    result = await sector_service.get_sector_info(sector_key)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/sector/{sector_key}/{symbol}")
async def get_sector_company(sector_key: str, symbol: str):
    """Get sector company details (Indian NSE/BSE only)"""
    sector_service = SectorService()
    result = await sector_service.get_sector_company(sector_key, symbol)
    
    if "error" in result:
        if "Not an Indian" in result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/industry/{industry_key}")
async def get_industry_info(industry_key: str):
    """Get industry information"""
    sector_service = SectorService()
    result = await sector_service.get_industry_info(industry_key)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/industry/{industry_key}/{symbol}")
async def get_industry_company(industry_key: str, symbol: str):
    """Get industry company details (Indian NSE/BSE only)"""
    sector_service = SectorService()
    result = await sector_service.get_industry_company(industry_key, symbol)
    
    if "error" in result:
        if "Not an Indian" in result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
