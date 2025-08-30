import yfinance as yf
from typing import Optional, Dict, Any
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json

class FundService:
    async def get_funds_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive fund data (for ETFs/Mutual Funds)"""
        cache_key = f"funds_data:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            funds_data = ticker.funds_data
            if not funds_data:
                return {"error": "Not a fund or fund data not available"}
            
            response = {
                'description': funds_data.description,
                'fund_overview': sanitize_for_json(funds_data.fund_overview.to_dict()) if hasattr(funds_data.fund_overview, 'to_dict') else funds_data.fund_overview,
                'fund_operations': sanitize_for_json(funds_data.fund_operations.to_dict()) if hasattr(funds_data.fund_operations, 'to_dict') else funds_data.fund_operations,
                'asset_classes': sanitize_for_json(funds_data.asset_classes.to_dict()) if hasattr(funds_data.asset_classes, 'to_dict') else funds_data.asset_classes,
                'top_holdings': sanitize_for_json(funds_data.top_holdings.to_dict()) if hasattr(funds_data.top_holdings, 'to_dict') else funds_data.top_holdings,
                'equity_holdings': sanitize_for_json(funds_data.equity_holdings.to_dict()) if hasattr(funds_data.equity_holdings, 'to_dict') else funds_data.equity_holdings,
                'bond_holdings': sanitize_for_json(funds_data.bond_holdings.to_dict()) if hasattr(funds_data.bond_holdings, 'to_dict') else funds_data.bond_holdings,
                'bond_ratings': sanitize_for_json(funds_data.bond_ratings.to_dict()) if hasattr(funds_data.bond_ratings, 'to_dict') else funds_data.bond_ratings,
                'sector_weightings': sanitize_for_json(funds_data.sector_weightings.to_dict()) if hasattr(funds_data.sector_weightings, 'to_dict') else funds_data.sector_weightings
            }
            
            # Cache for 24 hours
            await redis_client.set(cache_key, response, ttl=86400)
            return response
            
        except Exception as e:
            return {"error": f"Failed to get fund data: {str(e)}"}
    
    async def get_fund_top_holdings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get fund top holdings only"""
        cache_key = f"fund_top_holdings:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            funds_data = ticker.funds_data
            if not funds_data:
                return {"error": "Not a fund or fund data not available"}
            
            top_holdings = funds_data.top_holdings
            result = sanitize_for_json(top_holdings.to_dict() if hasattr(top_holdings, 'to_dict') else top_holdings)
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get fund top holdings: {str(e)}"}
    
    async def get_fund_sector_weightings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get fund sector weightings only"""
        cache_key = f"fund_sector_weightings:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            funds_data = ticker.funds_data
            if not funds_data:
                return {"error": "Not a fund or fund data not available"}
            
            sector_weightings = funds_data.sector_weightings
            result = sanitize_for_json(sector_weightings.to_dict() if hasattr(sector_weightings, 'to_dict') else sector_weightings)
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get fund sector weightings: {str(e)}"}
