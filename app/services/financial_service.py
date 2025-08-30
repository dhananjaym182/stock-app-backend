import yfinance as yf
from typing import Optional, Dict, Any
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, sanitize_for_json
import pandas as pd
class FinancialService:
    async def get_income_statement(self, symbol: str, quarterly: bool = False) -> Optional[Dict[str, Any]]:
        """Get income statement"""
        cache_key = f"income_stmt:{'quarterly' if quarterly else 'annual'}:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            if quarterly:
                stmt = ticker.quarterly_income_stmt
            else:
                stmt = ticker.income_stmt
            
            result = sanitize_for_json(stmt)
            
            # Cache for 24 hours (annual) or 6 hours (quarterly)
            ttl = 21600 if quarterly else 86400
            await redis_client.set(cache_key, result, ttl=ttl)
            return result
            
        except Exception as e:
            print(f"Error getting income statement for {symbol}: {e}")
            return None
    
    async def get_balance_sheet(self, symbol: str, quarterly: bool = False) -> Optional[Dict[str, Any]]:
        """Get balance sheet"""
        cache_key = f"balance_sheet:{'quarterly' if quarterly else 'annual'}:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            if quarterly:
                sheet = ticker.quarterly_balance_sheet
            else:
                sheet = ticker.balance_sheet
            
            result = sanitize_for_json(sheet)
            
            # Cache for 24 hours (annual) or 6 hours (quarterly)
            ttl = 21600 if quarterly else 86400
            await redis_client.set(cache_key, result, ttl=ttl)
            return result
            
        except Exception as e:
            print(f"Error getting balance sheet for {symbol}: {e}")
            return None
    
    async def get_cashflow(self, symbol: str, quarterly: bool = False) -> Optional[Dict[str, Any]]:
        """Get cash flow statement"""
        cache_key = f"cashflow:{'quarterly' if quarterly else 'annual'}:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            if quarterly:
                cf = ticker.quarterly_cashflow
            else:
                cf = ticker.cashflow
            
            result = sanitize_for_json(cf)
            
            # Cache for 24 hours (annual) or 6 hours (quarterly)
            ttl = 21600 if quarterly else 86400
            await redis_client.set(cache_key, result, ttl=ttl)
            return result
            
        except Exception as e:
            print(f"Error getting cashflow for {symbol}: {e}")
            return None
    
    async def get_financials(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive financials with enhanced caching"""
        cache_key = f"financials_comprehensive:{symbol.upper()}"
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, _, _ = get_safe_ticker_data_sync(symbol)
            if not ticker:
                return None
            
            try:
                info = ticker.info
            except Exception:
                info = {}
            
            financials = {}
            try:
                # Get all financial statements
                if hasattr(ticker, 'financials') and ticker.financials is not None and not ticker.financials.empty:
                    fin_dict = ticker.financials.to_dict()
                    financials['income_statement'] = {
                        str(k): {str(k2): float(v2) if pd.notna(v2) else None for k2, v2 in v.items()}
                        for k, v in fin_dict.items()
                    }
                
                if hasattr(ticker, 'balance_sheet') and ticker.balance_sheet is not None and not ticker.balance_sheet.empty:
                    bs_dict = ticker.balance_sheet.to_dict()
                    financials['balance_sheet'] = {
                        str(k): {str(k2): float(v2) if pd.notna(v2) else None for k2, v2 in v.items()}
                        for k, v in bs_dict.items()
                    }
                
                if hasattr(ticker, 'cashflow') and ticker.cashflow is not None and not ticker.cashflow.empty:
                    cf_dict = ticker.cashflow.to_dict()
                    financials['cashflow'] = {
                        str(k): {str(k2): float(v2) if pd.notna(v2) else None for k2, v2 in v.items()}
                        for k, v in cf_dict.items()
                    }
                    
            except Exception as e:
                print(f"Error processing financial statements: {e}")
                financials = {}
            
            def safe_get(value, multiplier=1):
                if value is None or pd.isna(value):
                    return None
                try:
                    return float(value) * multiplier
                except (ValueError, TypeError):
                    return None
            
            response = {
                'marketCap': safe_get(info.get('marketCap')),
                'peRatio': safe_get(info.get('trailingPE')),
                'volume': safe_get(info.get('regularMarketVolume') or info.get('volume')),
                'dividendYield': safe_get(info.get('dividendYield'), 100),
                'eps': safe_get(info.get('trailingEps')),
                'bookValue': safe_get(info.get('bookValue')),
                'debtToEquity': safe_get(info.get('debtToEquity')),
                'roe': safe_get(info.get('returnOnEquity'), 100),
                'roa': safe_get(info.get('returnOnAssets'), 100),
                'currentRatio': safe_get(info.get('currentRatio')),
                'quickRatio': safe_get(info.get('quickRatio')),
                'grossMargin': safe_get(info.get('grossMargins'), 100),
                'operatingMargin': safe_get(info.get('operatingMargins'), 100),
                'netMargin': safe_get(info.get('profitMargins'), 100),
                'revenueGrowth': safe_get(info.get('revenueGrowth'), 100),
                'earningsGrowth': safe_get(info.get('earningsGrowth'), 100),
                'beta': safe_get(info.get('beta')),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'fullTimeEmployees': safe_get(info.get('fullTimeEmployees')),
                'financialStatements': financials
            }
            
            result = sanitize_for_json(response)
            
            # Cache for 1 hour
            await redis_client.set(cache_key, result, ttl=3600)
            return result
            
        except Exception as e:
            print(f"Error getting financials for {symbol}: {e}")
            return None
