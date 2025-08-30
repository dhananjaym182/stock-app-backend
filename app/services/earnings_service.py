import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json

class EarningsService:
    def _safe_to_dict(self, df):
        """Convert DataFrame to dict safely; return None if empty"""
        if df is None or df.empty:
            return None
        
        # Convert index and columns to strings to avoid Timestamp serialization issues
        df_copy = df.copy()
        df_copy.index = df_copy.index.map(str)
        df_copy.columns = df_copy.columns.map(str)
        
        return sanitize_for_json(df_copy.to_dict())
    
    async def get_earnings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get annual earnings (Net Income)"""
        cache_key = f"earnings_annual:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            df = ticker.income_stmt
            if df is None or df.empty:
                return {"error": "No earnings data available"}
            
            net_income = df.loc[['Net Income']] if 'Net Income' in df.index else df
            result = {
                'symbol': symbol.upper(), 
                'earnings': self._safe_to_dict(net_income)
            }
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get earnings: {str(e)}"}
    
    async def get_quarterly_earnings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quarterly earnings (Net Income)"""
        cache_key = f"earnings_quarterly:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            df = ticker.quarterly_income_stmt
            if df is None or df.empty:
                return {"error": "No quarterly earnings data available"}
            
            net_income = df.loc[['Net Income']] if 'Net Income' in df.index else df
            result = {
                'symbol': symbol.upper(),
                'quarterly_earnings': self._safe_to_dict(net_income)
            }
            
            # Cache for 6 hours
            await redis_client.set(cache_key, result, ttl=21600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get quarterly earnings: {str(e)}"}
    
    async def get_earnings_dates(self, symbol: str, limit: int = 12) -> Optional[Dict[str, Any]]:
        """Get earnings dates (future and historical)"""
        cache_key = f"earnings_dates:{symbol.upper()}:{limit}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            df = ticker.get_earnings_dates(limit=limit)
            if df is None or df.empty:
                return {"error": "No earnings dates available"}
            
            result = {
                'symbol': symbol.upper(),
                'earnings_dates': self._safe_to_dict(df)
            }
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get earnings dates: {str(e)}"}
    
    async def get_revenue_estimate(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get revenue estimates"""
        cache_key = f"revenue_estimate:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            df = ticker.revenue_estimate
            if df is None or df.empty:
                return {"error": "No revenue estimate available"}
            
            result = {
                'symbol': symbol.upper(),
                'revenue_estimate': self._safe_to_dict(df)
            }
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get revenue estimate: {str(e)}"}
    
    async def get_eps_revisions(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get EPS revisions"""
        cache_key = f"eps_revisions:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            df = ticker.eps_revisions
            if df is None or df.empty:
                return {"error": "No EPS revisions data available"}
            
            result = {
                'symbol': symbol.upper(),
                'eps_revisions': self._safe_to_dict(df)
            }
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get EPS revisions: {str(e)}"}
    
    async def get_growth_estimates(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get growth estimates"""
        cache_key = f"growth_estimates:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            df = ticker.growth_estimates
            if df is None or df.empty:
                return {"error": "No growth estimates available"}
            
            result = {
                'symbol': symbol.upper(),
                'growth_estimates': self._safe_to_dict(df)
            }
            
            # Cache for 4 hours
            await redis_client.set(cache_key, result, ttl=14400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get growth estimates: {str(e)}"}
