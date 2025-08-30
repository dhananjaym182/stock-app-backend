import yfinance as yf
from typing import Optional, Dict, Any, List
from app.core.redis_client import redis_client
from app.core.config import settings
from app.utils.yfinance_helper import sanitize_for_json

AVAILABLE_MARKETS = ['US', 'GB', 'ASIA', 'EUROPE', 'RATES', 'COMMODITIES', 'CURRENCIES', 'CRYPTOCURRENCIES']

class MarketService:
    async def get_market_status(self, market_name: str) -> Optional[Dict[str, Any]]:
        """Get market status with caching"""
        cache_key = f"market_status:{market_name.upper()}"
        
        # Check cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            market = yf.Market(market_name.upper())
            status = market.status
            
            result = sanitize_for_json(status)
            
            # Cache for 5 minutes
            await redis_client.set(cache_key, result, ttl=300)
            return result
            
        except Exception as e:
            print(f"Error getting market status for {market_name}: {e}")
            return None
    
    async def get_market_summary(self, market_name: str) -> Optional[Dict[str, Any]]:
        """Get market summary with caching"""
        cache_key = f"market_summary:{market_name.upper()}"
        
        # Check cache first  
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            market = yf.Market(market_name.upper())
            summary = market.summary
            
            result = sanitize_for_json(summary)
            
            # Cache for 15 minutes
            await redis_client.set(cache_key, result, ttl=900)
            return result
            
        except Exception as e:
            print(f"Error getting market summary for {market_name}: {e}")
            return None
    
    async def bulk_download(self, tickers: str, period: str = "1mo", interval: str = "1d") -> Optional[Dict[str, Any]]:
        """Bulk download data for multiple tickers"""
        cache_key = f"bulk_download:{hash(tickers)}:{period}:{interval}"
        
        # Check cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Split tickers by space or comma
            ticker_list = [t.strip() for t in tickers.replace(',', ' ').split() if t.strip()]
            
            if len(ticker_list) > 50:  # Limit to prevent abuse
                return {"error": "Maximum 50 tickers allowed"}
            
            data = yf.download(ticker_list, period=period, interval=interval, group_by='ticker')
            result = sanitize_for_json(data.to_dict())
            
            # Cache for 30 minutes
            await redis_client.set(cache_key, result, ttl=1800)
            return result
            
        except Exception as e:
            print(f"Error in bulk download: {e}")
            return None
    
    def get_available_markets(self) -> Dict[str, Any]:
        """Get list of available markets"""
        return {
            'markets': AVAILABLE_MARKETS,
            'description': {
                'US': 'United States market',
                'GB': 'Great Britain market', 
                'ASIA': 'Asian markets',
                'EUROPE': 'European markets',
                'RATES': 'Interest rates',
                'COMMODITIES': 'Commodities market',
                'CURRENCIES': 'Currency exchange rates',
                'CRYPTOCURRENCIES': 'Cryptocurrency market'
            }
        }
