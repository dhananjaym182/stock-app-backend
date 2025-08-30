import yfinance as yf
from typing import Optional, Dict, Any, List
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json
from datetime import datetime

class OptionsService:
    async def get_options_expiration_dates(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get available options expiration dates"""
        cache_key = f"options_expiry:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            options = ticker.options
            result = {'expiration_dates': list(options) if options else []}
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get options dates: {str(e)}"}
    
    async def get_option_chain(self, symbol: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get option chain for specific expiration date"""
        cache_key = f"option_chain:{symbol.upper()}:{date or 'first'}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            if date:
                option_chain = ticker.option_chain(date)
            else:
                # Get first available expiration date
                if ticker.options:
                    option_chain = ticker.option_chain(ticker.options[0])
                else:
                    return {"error": "No options available"}
            
            result = {
                'calls': sanitize_for_json(option_chain.calls.to_dict()),
                'puts': sanitize_for_json(option_chain.puts.to_dict())
            }
            
            # Cache for 30 minutes
            await redis_client.set(cache_key, result, ttl=1800)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get option chain: {str(e)}"}
    
    async def get_calls_only(self, symbol: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get only call options for specific expiration date"""
        cache_key = f"calls_only:{symbol.upper()}:{date or 'first'}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            if date:
                option_chain = ticker.option_chain(date)
            else:
                if ticker.options:
                    option_chain = ticker.option_chain(ticker.options[0])
                else:
                    return {"error": "No options available"}
            
            result = sanitize_for_json(option_chain.calls.to_dict())
            
            # Cache for 30 minutes
            await redis_client.set(cache_key, result, ttl=1800)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get calls: {str(e)}"}
    
    async def get_puts_only(self, symbol: str, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get only put options for specific expiration date"""
        cache_key = f"puts_only:{symbol.upper()}:{date or 'first'}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return {"error": "Symbol not found"}
            
            if date:
                option_chain = ticker.option_chain(date)
            else:
                if ticker.options:
                    option_chain = ticker.option_chain(ticker.options[0])
                else:
                    return {"error": "No options available"}
            
            result = sanitize_for_json(option_chain.puts.to_dict())
            
            # Cache for 30 minutes
            await redis_client.set(cache_key, result, ttl=1800)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get puts: {str(e)}"}
