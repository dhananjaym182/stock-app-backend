import yfinance as yf
from typing import Optional, Dict, Any
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import sanitize_for_json

class ScreeningService:
    async def equity_screen(self, criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Screen equities based on criteria"""
        cache_key = f"equity_screen:{hash(str(sorted(criteria.items())))}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Build query based on provided criteria
            query = yf.EquityQuery()
            
            # Add filters based on request data
            if 'region' in criteria:
                query = query.region(criteria['region'])
            
            if 'sector' in criteria:
                query = query.sector(criteria['sector'])
            
            if 'exchange' in criteria:
                query = query.exchange(criteria['exchange'])
            
            if 'market_cap_min' in criteria:
                query = query.market_cap('>', criteria['market_cap_min'])
            
            if 'market_cap_max' in criteria:
                query = query.market_cap('<', criteria['market_cap_max'])
            
            if 'pe_ratio_min' in criteria:
                query = query.pe_ratio('>', criteria['pe_ratio_min'])
            
            if 'pe_ratio_max' in criteria:
                query = query.pe_ratio('<', criteria['pe_ratio_max'])
            
            # Execute screen
            offset = criteria.get('offset', 0)
            size = criteria.get('size', 25)
            count = criteria.get('count', 100)
            
            screener = yf.Screener(query, offset=offset, size=size, count=count)
            results = screener.response
            
            result = sanitize_for_json(results)
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {"error": f"Equity screening failed: {str(e)}"}
    
    async def fund_screen(self, criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Screen funds based on criteria"""
        cache_key = f"fund_screen:{hash(str(sorted(criteria.items())))}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Build query based on provided criteria
            query = yf.FundQuery()
            
            # Add filters based on request data
            if 'region' in criteria:
                query = query.region(criteria['region'])
            
            if 'fund_type' in criteria:
                query = query.fund_type(criteria['fund_type'])
            
            if 'expense_ratio_max' in criteria:
                query = query.expense_ratio('<', criteria['expense_ratio_max'])
            
            # Execute screen
            offset = criteria.get('offset', 0)
            size = criteria.get('size', 25)
            count = criteria.get('count', 100)
            
            screener = yf.Screener(query, offset=offset, size=size, count=count)
            results = screener.response
            
            result = sanitize_for_json(results)
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            return {"error": f"Fund screening failed: {str(e)}"}
    
    def get_predefined_screens(self) -> Dict[str, Any]:
        """Get list of predefined screening criteria"""
        return {
            'equity_screens': {
                'large_cap_growth': 'Large cap growth stocks',
                'small_cap_value': 'Small cap value stocks',
                'dividend_aristocrats': 'Dividend aristocrat stocks',
                'momentum_stocks': 'High momentum stocks'
            },
            'fund_screens': {
                'low_cost_etfs': 'Low expense ratio ETFs',
                'sector_etfs': 'Sector-specific ETFs',
                'international_funds': 'International mutual funds'
            }
        }
