import yfinance as yf
from typing import Optional, Dict, Any
import logging

from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json

logger = logging.getLogger(__name__)

class TickerService:
    
    async def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive ticker info with enhanced error handling"""
        cache_key = f"ticker_info:{symbol.upper()}"
        
        try:
            # Check cache first
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Ticker info cache hit for {symbol}")
                return cached_data

            # Fetch data using your helper function
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                logger.warning(f"No ticker data found for {symbol}")
                return None

            # Get info with enhanced error handling
            try:
                info = ticker.info
                if not info or len(info) < 3:  # Basic validation
                    logger.warning(f"Empty or invalid ticker info for {symbol}")
                    return None
                    
            except Exception as info_error:
                logger.error(f"Failed to get ticker info for {symbol}: {info_error}")
                return None

            result = sanitize_for_json(info)
            
            # Cache for 30 minutes
            await redis_client.set(cache_key, result, ttl=1800)
            logger.info(f"Ticker info successfully fetched and cached for {symbol}")
            return result

        except Exception as e:
            logger.error(f"Error getting ticker info for {symbol}: {e}")
            return None

    async def get_fast_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get fast ticker info with enhanced error handling"""
        cache_key = f"ticker_fast_info:{symbol.upper()}"
        
        try:
            # Check cache first (short TTL for fast info)
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Fast info cache hit for {symbol}")
                return cached_data

            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                logger.warning(f"No ticker data found for fast info: {symbol}")
                return None

            try:
                fast_info = ticker.fast_info
                
                # Convert FastInfo object to dict safely
                if hasattr(fast_info, "to_dict"):
                    result = sanitize_for_json(fast_info.to_dict())
                else:
                    result = sanitize_for_json(dict(fast_info))
                    
            except Exception as fast_error:
                logger.error(f"Failed to get fast info for {symbol}: {fast_error}")
                return None

            # Cache for 1 minute (fast info should be fresh)
            await redis_client.set(cache_key, result, ttl=60)
            logger.info(f"Fast info successfully fetched for {symbol}")
            return result

        except Exception as e:
            logger.error(f"Error getting fast info for {symbol}: {e}")
            return None

    async def get_actions(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get dividends and stock splits with enhanced error handling"""
        cache_key = f"ticker_actions:{symbol.upper()}"
        
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data

            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None

            try:
                actions = ticker.actions
                if actions is None or actions.empty:
                    logger.info(f"No actions data for {symbol}")
                    return {"actions": {}, "message": "No actions data available"}
                    
                result = sanitize_for_json(actions.to_dict())
                
            except Exception as actions_error:
                logger.error(f"Failed to get actions for {symbol}: {actions_error}")
                return None

            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"Error getting actions for {symbol}: {e}")
            return None

    async def get_dividends(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get dividend history with enhanced error handling"""
        cache_key = f"ticker_dividends:{symbol.upper()}"
        
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data

            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None

            try:
                dividends = ticker.dividends
                if dividends is None or dividends.empty:
                    logger.info(f"No dividends data for {symbol}")
                    return {"dividends": {}, "message": "No dividend history available"}
                    
                result = sanitize_for_json(dividends.to_dict())
                
            except Exception as div_error:
                logger.error(f"Failed to get dividends for {symbol}: {div_error}")
                return None

            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"Error getting dividends for {symbol}: {e}")
            return None

    async def get_splits(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock split history with enhanced error handling"""
        cache_key = f"ticker_splits:{symbol.upper()}"
        
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data

            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None

            try:
                splits = ticker.splits
                if splits is None or splits.empty:
                    logger.info(f"No splits data for {symbol}")
                    return {"splits": {}, "message": "No stock split history available"}
                    
                result = sanitize_for_json(splits.to_dict())
                
            except Exception as split_error:
                logger.error(f"Failed to get splits for {symbol}: {split_error}")
                return None

            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"Error getting splits for {symbol}: {e}")
            return None

    async def get_calendar(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get upcoming events calendar with enhanced error handling"""
        cache_key = f"ticker_calendar:{symbol.upper()}"
        
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data

            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None

            try:
                calendar = ticker.calendar
                if calendar is None:
                    logger.info(f"No calendar data for {symbol}")
                    return {"calendar": {}, "message": "No calendar events available"}
                    
                result = sanitize_for_json(calendar)
                
            except Exception as cal_error:
                logger.error(f"Failed to get calendar for {symbol}: {cal_error}")
                return None

            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"Error getting calendar for {symbol}: {e}")
            return None

    async def get_sustainability(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get sustainability scores with enhanced error handling"""
        cache_key = f"ticker_sustainability:{symbol.upper()}"
        
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data

            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None

            try:
                sustainability = ticker.sustainability
                
                if sustainability is not None:
                    result = sanitize_for_json(sustainability.to_dict())
                else:
                    logger.info(f"No sustainability data for {symbol}")
                    result = {"sustainability": {}, "message": "No sustainability data available"}
                    
            except Exception as sus_error:
                logger.error(f"Failed to get sustainability for {symbol}: {sus_error}")
                return {"sustainability": {}, "message": "Sustainability data unavailable"}

            # Cache for 24 hours
            await redis_client.set(cache_key, result, ttl=86400)
            return result

        except Exception as e:
            logger.error(f"Error getting sustainability for {symbol}: {e}")
            return None
