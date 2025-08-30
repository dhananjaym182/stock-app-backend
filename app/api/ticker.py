from fastapi import APIRouter, HTTPException
from app.services.ticker_service import TickerService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/ticker/{symbol}/info")
async def get_ticker_info(symbol: str):
    """Get comprehensive ticker info"""
    logger.info(f"Ticker info request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_ticker_info(symbol)
        
        if result is None:
            logger.warning(f"Ticker info not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        logger.info(f"Ticker info successfully fetched for: {symbol}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_ticker_info for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticker info: {str(e)}")

@router.get("/ticker/{symbol}/fast_info")
async def get_fast_info(symbol: str):
    """Get fast ticker info"""
    logger.info(f"Fast info request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_fast_info(symbol)
        
        if result is None:
            logger.warning(f"Fast info not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_fast_info for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get fast info: {str(e)}")

@router.get("/ticker/{symbol}/actions")
async def get_actions(symbol: str):
    """Get dividends and stock splits"""
    logger.info(f"Actions request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_actions(symbol)
        
        if result is None:
            logger.warning(f"Actions not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_actions for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get actions: {str(e)}")

@router.get("/ticker/{symbol}/dividends")
async def get_dividends(symbol: str):
    """Get dividend history"""
    logger.info(f"Dividends request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_dividends(symbol)
        
        if result is None:
            logger.warning(f"Dividends not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_dividends for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dividends: {str(e)}")

@router.get("/ticker/{symbol}/splits")
async def get_splits(symbol: str):
    """Get stock split history"""
    logger.info(f"Splits request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_splits(symbol)
        
        if result is None:
            logger.warning(f"Splits not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_splits for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get splits: {str(e)}")

@router.get("/ticker/{symbol}/calendar")
async def get_calendar(symbol: str):
    """Get upcoming events calendar"""
    logger.info(f"Calendar request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_calendar(symbol)
        
        if result is None:
            logger.warning(f"Calendar not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_calendar for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get calendar: {str(e)}")

@router.get("/ticker/{symbol}/sustainability")
async def get_sustainability(symbol: str):
    """Get sustainability scores"""
    logger.info(f"Sustainability request for: {symbol}")
    
    try:
        ticker_service = TickerService()
        result = await ticker_service.get_sustainability(symbol)
        
        if result is None:
            logger.warning(f"Sustainability not found for: {symbol}")
            raise HTTPException(status_code=404, detail='Symbol not found')
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_sustainability for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sustainability: {str(e)}")

# Test endpoint
@router.get("/ticker/test")
async def test_ticker_router():
    """Test endpoint to verify ticker router is working"""
    return {
        "message": "Ticker router is working perfectly!",
        "timestamp": datetime.now().isoformat(),
        "router": "ticker",
        "status": "active"
    }
