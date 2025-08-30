import yfinance as yf
from typing import Optional, Dict, Any
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json

class YfinanceAnalysisService:
    def _safe_to_dict(self, data):
        """Convert DataFrame or dict to dict safely; return empty dict if None/empty"""
        if data is None:
            return {}
        
        # If DataFrame, convert to dict
        if hasattr(data, "to_dict"):
            return sanitize_for_json(data.to_dict())
        
        # If already dict, just return sanitized
        if isinstance(data, dict):
            return sanitize_for_json(data)
        
        return {}
    
    async def get_analyst_price_targets(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get analyst price targets"""
        cache_key = f"analyst_price_targets:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.analyst_price_targets)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get analyst price targets: {str(e)}"}
    
    async def get_recommendations(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get analyst recommendations"""
        cache_key = f"yfinance_recommendations:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.recommendations)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get recommendations: {str(e)}"}
    
    async def get_recommendations_summary(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get recommendations summary"""
        cache_key = f"recommendations_summary:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.recommendations_summary)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get recommendations summary: {str(e)}"}
    
    async def get_upgrades_downgrades(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get upgrades and downgrades"""
        cache_key = f"upgrades_downgrades:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.upgrades_downgrades)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get upgrades/downgrades: {str(e)}"}
    
    async def get_earnings_estimates(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get earnings estimates"""
        cache_key = f"earnings_estimates:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.earnings_estimates)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get earnings estimates: {str(e)}"}
    
    async def get_financial_estimates(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get financial estimates"""
        cache_key = f"financial_estimates:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.financial_estimates)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get financial estimates: {str(e)}"}
    
    async def get_sustainability(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get sustainability data"""
        cache_key = f"yfinance_sustainability:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            result = self._safe_to_dict(ticker.sustainability)
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get sustainability data: {str(e)}"}
