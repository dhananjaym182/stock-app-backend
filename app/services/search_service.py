import yfinance as yf
from typing import Optional, Dict, Any, List
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import sanitize_for_json

class SearchService:
    async def search_symbols(
        self, 
        query: str, 
        max_results: int = 10, 
        news_count: int = 5, 
        include_research: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Enhanced search for stocks and news"""
        cache_key = f"search_enhanced:{query}:{max_results}:{news_count}:{include_research}"
        
        # Check cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            search_result = yf.Search(
                query,
                max_results=max_results,
                news_count=news_count,
                include_research=include_research
            )
            
            response = {
                'quotes': sanitize_for_json(search_result.quotes),
                'news': sanitize_for_json(search_result.news)
            }
            
            if include_research:
                response['research'] = sanitize_for_json(search_result.research)
            
            # Cache for 5 minutes
            await redis_client.set(cache_key, response, ttl=300)
            return response
            
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return None
    
    async def lookup_ticker(
        self, 
        query: str, 
        lookup_type: str = "all", 
        count: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Advanced ticker lookup"""
        cache_key = f"lookup:{query}:{lookup_type}:{count}"
        
        # Check cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            lookup_result = yf.Lookup(query)
            
            if lookup_type == 'all':
                result = lookup_result.get_all(count=count)
            elif lookup_type == 'stock':
                result = lookup_result.get_stock(count=count)
            elif lookup_type == 'etf':
                result = lookup_result.get_etf(count=count)
            elif lookup_type == 'mutualfund':
                result = lookup_result.get_mutualfund(count=count)
            elif lookup_type == 'index':
                result = lookup_result.get_index(count=count)
            elif lookup_type == 'future':
                result = lookup_result.get_future(count=count)
            elif lookup_type == 'currency':
                result = lookup_result.get_currency(count=count)
            elif lookup_type == 'cryptocurrency':
                result = lookup_result.get_cryptocurrency(count=count)
            else:
                return {"error": "Invalid lookup type"}
            
            sanitized_result = sanitize_for_json(result)
            
            # Cache for 2 hours
            await redis_client.set(cache_key, sanitized_result, ttl=7200)
            return sanitized_result
            
        except Exception as e:
            print(f"Lookup error for query '{query}': {e}")
            return None
    
    def get_lookup_types(self) -> Dict[str, Any]:
        """Get available lookup types"""
        return {
            'types': ['all', 'stock', 'etf', 'mutualfund', 'index', 'future', 'currency', 'cryptocurrency'],
            'description': {
                'all': 'All available instruments',
                'stock': 'Stocks only',
                'etf': 'Exchange-traded funds',
                'mutualfund': 'Mutual funds',
                'index': 'Market indices',
                'future': 'Futures contracts',
                'currency': 'Currency pairs',
                'cryptocurrency': 'Cryptocurrencies'
            }
        }
