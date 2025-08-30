import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any, List
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import sanitize_for_json

class SectorService:
    def _filter_indian_tickers(self, tickers_df):
        """Filter DataFrame for NSE/BSE Indian tickers only"""
        if tickers_df is None or tickers_df.empty:
            return []
        
        if isinstance(tickers_df, pd.DataFrame) and 'symbol' in tickers_df.columns:
            indian_df = tickers_df[tickers_df['symbol'].str.endswith(('.NS', '.BO'))]
            return indian_df.to_dict(orient='records')
        
        return tickers_df.to_dict(orient='records') if isinstance(tickers_df, pd.DataFrame) else tickers_df
    
    async def get_sector_info(self, sector_key: str) -> Optional[Dict[str, Any]]:
        """Get sector information"""
        cache_key = f"sector_info:{sector_key}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            sector = yf.Sector(sector_key)
            response = {
                'key': sector.key,
                'name': sector.name,
                'symbol': sector.symbol,
                'overview': sanitize_for_json(sector.overview),
                'industries': sanitize_for_json(sector.industries),
                'top_companies': self._filter_indian_tickers(sector.top_companies),
            }
            
            # Cache for 24 hours
            await redis_client.set(cache_key, response, ttl=86400)
            return response
            
        except Exception as e:
            return {"error": f"Failed to get sector info: {str(e)}"}
    
    async def get_sector_company(self, sector_key: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Get sector company details (Indian NSE/BSE only)"""
        cache_key = f"sector_company:{sector_key}:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            symbol = symbol.upper()
            
            # Validate exchange
            if not symbol.endswith(('.NS', '.BO')):
                return {"error": "Not an Indian NSE/BSE ticker"}
            
            ticker = yf.Ticker(symbol)
            info = sanitize_for_json(ticker.info)
            history = sanitize_for_json(ticker.history(period='1mo').to_dict())
            
            result = {
                'symbol': symbol,
                'info': info,
                'history': history
            }
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get sector company: {str(e)}"}
    
    async def get_industry_info(self, industry_key: str) -> Optional[Dict[str, Any]]:
        """Get industry information"""
        cache_key = f"industry_info:{industry_key}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            industry = yf.Industry(industry_key)
            response = {
                'key': industry.key,
                'name': industry.name,
                'sector_key': industry.sector_key,
                'sector_name': industry.sector_name,
                'overview': sanitize_for_json(industry.overview),
                'top_companies': self._filter_indian_tickers(industry.top_companies),
            }
            
            # Cache for 24 hours
            await redis_client.set(cache_key, response, ttl=86400)
            return response
            
        except Exception as e:
            return {"error": f"Failed to get industry info: {str(e)}"}
    
    async def get_industry_company(self, industry_key: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Get industry company details (Indian NSE/BSE only)"""
        cache_key = f"industry_company:{industry_key}:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            symbol = symbol.upper()
            
            if not symbol.endswith(('.NS', '.BO')):
                return {"error": "Not an Indian NSE/BSE ticker"}
            
            ticker = yf.Ticker(symbol)
            info = sanitize_for_json(ticker.info)
            history = sanitize_for_json(ticker.history(period='1mo').to_dict())
            
            result = {
                'symbol': symbol,
                'info': info,
                'history': history
            }
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {"error": f"Failed to get industry company: {str(e)}"}
