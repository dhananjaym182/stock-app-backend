import yfinance as yf
from typing import Optional, Dict, Any
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json

class HoldersService:
    async def get_major_holders(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get major holders"""
        cache_key = f"major_holders:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            major_holders = ticker.major_holders
            result = sanitize_for_json(major_holders.to_dict())
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get major holders: {str(e)}"}
    
    async def get_institutional_holders(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get institutional holders"""
        cache_key = f"institutional_holders:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            institutional_holders = ticker.institutional_holders
            result = sanitize_for_json(institutional_holders.to_dict())
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get institutional holders: {str(e)}"}
    
    async def get_mutualfund_holders(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get mutual fund holders"""
        cache_key = f"mutualfund_holders:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            mutualfund_holders = ticker.mutualfund_holders
            result = sanitize_for_json(mutualfund_holders.to_dict())
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get mutual fund holders: {str(e)}"}
    
    async def get_insider_purchases(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get insider purchases"""
        cache_key = f"insider_purchases:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            insider_purchases = ticker.insider_purchases
            result = sanitize_for_json(insider_purchases.to_dict())
            
            # Cache for 6 hours
            await redis_client.set(cache_key, result, ttl=21600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get insider purchases: {str(e)}"}
    
    async def get_insider_transactions(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get insider transactions"""
        cache_key = f"insider_transactions:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            insider_transactions = ticker.insider_transactions
            result = sanitize_for_json(insider_transactions.to_dict())
            
            # Cache for 6 hours
            await redis_client.set(cache_key, result, ttl=21600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get insider transactions: {str(e)}"}
    
    async def get_insider_roster_holders(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get insider roster holders"""
        cache_key = f"insider_roster:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            insider_roster = ticker.insider_roster_holders
            result = sanitize_for_json(insider_roster.to_dict())
            
            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get insider roster: {str(e)}"}
