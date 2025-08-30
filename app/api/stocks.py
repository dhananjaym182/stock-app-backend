from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.services.stock_service import StockService
from app.schemas.stocks import (
    StockQuoteResponseWrapper, StockHistoryResponse,
    SearchResponse, RecommendationResponse, ErrorResponse
)  # FIXED: Added missing closing parenthesis
from app.utils.yfinance_helper import calculate_technical_recommendations, get_safe_ticker_data_sync

router = APIRouter()

@router.get("/quote/{symbol}", response_model=StockQuoteResponseWrapper)
async def get_stock_quote(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time stock quote - backward compatible with Flask API"""
    logger.info(f"Quote request received for symbol: {symbol}")
    
    try:
        stock_service = StockService(db)
        quote_data = await stock_service.get_quote(symbol)
        
        if not quote_data:
            logger.error(f"No quote data found for symbol: {symbol}")
            raise HTTPException(status_code=404, detail="Stock not found or no data available")
        
        logger.info(f"Quote data successfully fetched for: {symbol}")
        return quote_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/history/{symbol}", response_model=StockHistoryResponse)
async def get_stock_history(
    symbol: str,
    period: str = Query(default="6M", description="Time period: 1D, 1W, 15D, 1M, 6M, 1Y, 5Y, ALL"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical stock data - backward compatible with Flask API"""
    logger.info(f"History request received for symbol: {symbol}, period: {period}")
    
    try:
        stock_service = StockService(db)
        history_data = await stock_service.get_history(symbol, period)
        
        # Ensure proper response structure for Pydantic validation
        if not history_data:
            return {
                "data": [],
                "source": "error",
                "timestamp": datetime.now().isoformat(),
                "period": period,
                "records": 0,
                "error": "No historical data available"
            }
            
        # Handle error responses from service
        if "error" in history_data and history_data["error"]:
            logger.warning(f"Service returned error for {symbol}: {history_data['error']}")
            
        return history_data
        
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_history for {symbol}: {str(e)}")
        # Return proper structure instead of raising exception
        return {
            "data": [],
            "source": "error",
            "timestamp": datetime.now().isoformat(),
            "period": period,
            "records": 0,
            "error": f"Internal server error: {str(e)}"
        }

@router.get("/search", response_model=SearchResponse)
async def search_stocks(
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db)
):
    """Search stocks - backward compatible with Flask API"""
    logger.info(f"Search request received for query: {q}")
    
    try:
        stock_service = StockService(db)
        search_results = await stock_service.search_stocks(q)
        return search_results
    except Exception as e:
        logger.error(f"Search error for query '{q}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/recommendations/{symbol}", response_model=RecommendationResponse)
async def get_stock_recommendations(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """Get stock recommendations with technical analysis - backward compatible"""
    logger.info(f"Recommendations request for symbol: {symbol}")
    
    try:
        # Get stock info from database
        stock_service = StockService(db)
        yahoo_symbol = await stock_service._get_yahoo_symbol(symbol)
        
        if not yahoo_symbol:
            logger.error(f"Yahoo symbol not found for: {symbol}")
            raise HTTPException(status_code=404, detail="Stock not found")

        # Get technical data with enhanced error handling
        try:
            ticker, hist, working_symbol = get_safe_ticker_data_sync(yahoo_symbol)
        except Exception as e:
            logger.error(f"Error getting ticker data for {yahoo_symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch ticker data: {str(e)}")

        if ticker is None or hist is None or hist.empty:
            logger.error(f"No historical data found for symbol: {yahoo_symbol}")
            raise HTTPException(status_code=404, detail="No historical data found for this symbol")

        recommendations = calculate_technical_recommendations(hist, working_symbol)
        
        if 'error' in recommendations:
            logger.error(f"Technical analysis error for {symbol}: {recommendations['error']}")
            raise HTTPException(status_code=500, detail=recommendations['error'])

        logger.info(f"Recommendations successfully generated for: {symbol}")
        return recommendations

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in recommendations for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/stats")
async def get_api_stats(db: AsyncSession = Depends(get_db)):
    """Get API statistics - backward compatible with Flask API"""
    logger.info("API stats request received")
    
    try:
        from sqlalchemy import text
        from app.models.stocks import Stock, StockHistory

        # Count active stocks
        total_stocks_result = await db.execute(
            text("SELECT COUNT(*) FROM stocks WHERE is_active = TRUE")
        )
        total_stocks = total_stocks_result.scalar()

        # Count stocks with history
        stocks_with_history_result = await db.execute(
            text("SELECT COUNT(DISTINCT symbol) FROM stock_history")
        )
        stocks_with_history = stocks_with_history_result.scalar()

        # Count total history records
        total_history_result = await db.execute(
            text("SELECT COUNT(*) FROM stock_history")
        )
        total_history_records = total_history_result.scalar()

        # Recent updates
        recent_updates_result = await db.execute(text("""
            SELECT symbol, MAX(date) as latest_date, COUNT(*) as records
            FROM stock_history
            GROUP BY symbol
            ORDER BY latest_date DESC
            LIMIT 5
        """))
        recent_updates = recent_updates_result.fetchall()

        stats_data = {
            'total_stocks': total_stocks,
            'cached_items': 0,  # Redis cache items (can be implemented)
            'stocks_with_history': stocks_with_history,
            'total_history_records': total_history_records,
            'recent_updates': [
                {
                    'symbol': row[0],
                    'latest_date': row[1].isoformat() if row[1] else None,
                    'records': row[2]
                } for row in recent_updates
            ],
            'service': 'fastapi-yfinance-enhanced',
            'database': 'connected'
        }
        
        logger.info("API stats successfully generated")
        return stats_data

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

# Test endpoint for debugging
@router.get("/test")
async def test_stocks_router():
    """Test endpoint to verify stocks router is working"""
    return {
        "message": "Stocks router is working perfectly!",
        "timestamp": datetime.now().isoformat(),
        "router": "stocks",
        "status": "active"
    }
