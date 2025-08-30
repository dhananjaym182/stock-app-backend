import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from app.core.redis_client import redis_client
from app.core.config import settings
from app.models.stocks import Stock, StockHistory, CompanyInfo
from app.utils.yfinance_helper import get_safe_ticker_data_async, sanitize_for_json
import json
import logging

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time stock quote with intelligent caching"""
        cache_key = f"quote:{symbol.upper()}"
        
        try:
            # 1. Check Redis cache first
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Quote cache hit for {symbol}")
                return cached_data

            # 2. Check if we have recent data in database for off-market hours
            if not self._is_market_open():
                db_quote = await self._get_latest_db_quote(symbol)
                if db_quote:
                    await redis_client.set(cache_key, db_quote, ttl=settings.CACHE_TTL_REALTIME * 10)
                    logger.info(f"Using database quote for {symbol} (market closed)")
                    return db_quote

            # 3. Fetch from yfinance
            quote_data = await self._fetch_quote_from_yfinance(symbol)
            if quote_data:
                # Cache with different TTL based on market hours
                ttl = settings.CACHE_TTL_REALTIME if self._is_market_open() else settings.CACHE_TTL_REALTIME * 10
                await redis_client.set(cache_key, quote_data, ttl=ttl)
                logger.info(f"Fresh quote fetched for {symbol}")
                return quote_data

        except Exception as e:
            logger.error(f"Error in get_quote for {symbol}: {e}")

        return None

    async def get_history(self, symbol: str, period: str = "6M") -> Dict[str, Any]:
        """Get historical data with database-first approach"""
        cache_key = f"history:{symbol.upper()}:{period}"
        
        try:
            # 1. Check Redis cache
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.info(f"History cache hit for {symbol}:{period}")
                return cached_data

            # 2. Get yahoo symbol from database
            yahoo_symbol = await self._get_yahoo_symbol(symbol)
            if not yahoo_symbol:
                return {
                    "data": [],
                    "source": "error",
                    "timestamp": datetime.now().isoformat(),
                    "period": period,
                    "records": 0,
                    "error": "Symbol not found in database"
                }

            # 3. Check database for existing data
            start_date, end_date = self._get_period_dates(period)
            latest_db_date = await self._get_latest_date_in_db(symbol)

            # 4. Determine if we need to fetch new data
            need_fetch = False
            fetch_start_date = None
            
            if latest_db_date is None:
                need_fetch = True
                fetch_start_date = None  # Fetch all historical data
            elif latest_db_date < (date.today() - timedelta(days=1)):
                need_fetch = True
                fetch_start_date = latest_db_date + timedelta(days=1)

            # 5. Fetch missing data if needed
            if need_fetch:
                logger.info(f"Fetching new historical data for {symbol}")
                await self._fetch_and_store_history(yahoo_symbol, symbol, fetch_start_date)

            # 6. Get final data from database
            history_data = await self._get_history_from_db(symbol, start_date, end_date)

            response_data = {
                "data": history_data,
                "source": "database" if not need_fetch else "database+yfinance",
                "timestamp": datetime.now().isoformat(),
                "period": period,
                "records": len(history_data),
                "error": None
            }

            # Cache the response
            await redis_client.set(cache_key, response_data, ttl=settings.CACHE_TTL_HISTORICAL)
            logger.info(f"History data prepared for {symbol}: {len(history_data)} records")
            return response_data

        except Exception as e:
            logger.error(f"Error in get_history for {symbol}: {e}")
            return {
                "data": [],
                "source": "error",
                "timestamp": datetime.now().isoformat(),
                "period": period,
                "records": 0,
                "error": f"Failed to get historical data: {str(e)}"
            }

    async def search_stocks(self, query: str) -> Dict[str, Any]:
        """Search stocks in database"""
        cache_key = f"search:{query.upper()}"
        
        try:
            # Check cache first
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data

            # Search in database
            search_query = f"%{query.upper()}%"
            stmt = select(Stock).where(
                and_(
                    Stock.is_active == True,
                    (Stock.symbol.ilike(search_query) |
                     Stock.company_name.ilike(search_query) |
                     Stock.yahoo_symbol.ilike(search_query))
                )
            ).limit(20)

            result = await self.db.execute(stmt)
            stocks = result.scalars().all()

            response_data = {
                "stocks": [
                    {
                        "symbol": stock.symbol,
                        "yahoo_symbol": stock.yahoo_symbol,
                        "company_name": stock.company_name,
                        "exchange": stock.exchange,
                        "sector": stock.sector
                    }
                    for stock in stocks
                ],
                "source": "database",
                "total_results": len(stocks)
            }

            # Cache for 10 minutes
            await redis_client.set(cache_key, response_data, ttl=600)
            return response_data

        except Exception as e:
            logger.error(f"Search error for '{query}': {e}")
            return {
                "stocks": [],
                "source": "error",
                "total_results": 0,
                "error": f"Search failed: {str(e)}"
            }

    async def _get_yahoo_symbol(self, symbol: str) -> Optional[str]:
        """Get yahoo symbol from database"""
        try:
            stmt = select(Stock.yahoo_symbol).where(Stock.symbol == symbol.upper())
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting yahoo symbol for {symbol}: {e}")
            return None

    async def _get_latest_date_in_db(self, symbol: str) -> Optional[date]:
        """Get latest date in database for symbol"""
        try:
            stmt = select(StockHistory.date).where(
                StockHistory.symbol == symbol.upper()
            ).order_by(StockHistory.date.desc()).limit(1)
            
            result = await self.db.execute(stmt)
            latest_date = result.scalar_one_or_none()
            return latest_date.date() if latest_date else None
        except Exception as e:
            logger.error(f"Error getting latest date for {symbol}: {e}")
            return None

    async def _fetch_quote_from_yfinance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Enhanced yfinance fetching with multiple fallback methods"""
        try:
            # Get stock info from database first
            stmt = select(Stock).where(Stock.symbol == symbol.upper())
            result = await self.db.execute(stmt)
            stock_info = result.scalar_one_or_none()

            if not stock_info:
                logger.warning(f"Stock {symbol} not found in database")
                return None

            yahoo_symbol = stock_info.yahoo_symbol
            logger.info(f"Fetching yfinance data for {yahoo_symbol}")

            # Try multiple approaches for data fetching
            ticker = None
            hist = None
            
            try:
                # Method 1: Your existing helper
                ticker, hist, working_symbol = await get_safe_ticker_data_async(yahoo_symbol)
                if ticker and hist is not None and not hist.empty:
                    logger.info(f"Helper method successful for {yahoo_symbol}")
            except Exception as e:
                logger.warning(f"Helper method failed for {yahoo_symbol}: {e}")

            if ticker is None or hist is None or (hasattr(hist, 'empty') and hist.empty):
                try:
                    # Method 2: Direct yfinance with different periods
                    logger.info(f"Trying direct yfinance for {yahoo_symbol}")
                    ticker = yf.Ticker(yahoo_symbol)
                    
                    # Try different periods if 1d fails
                    for period in ["2d", "5d", "1mo"]:
                        try:
                            hist = ticker.history(period=period)
                            if hist is not None and not hist.empty:
                                logger.info(f"Success with period {period} for {yahoo_symbol}")
                                break
                        except Exception as pe:
                            logger.warning(f"Period {period} failed for {yahoo_symbol}: {pe}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Direct yfinance failed for {yahoo_symbol}: {e}")
                    return None

            # Validate we have data
            if hist is None or hist.empty:
                logger.error(f"No historical data available for {yahoo_symbol}")
                return None

            # Safely extract data
            current_price = float(hist['Close'].iloc[-1])
            previous_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            change = current_price - previous_price
            change_percent = (change / previous_price * 100) if previous_price != 0 else 0

            # Safely get info (this often causes the JSON parsing error)
            info = {}
            if ticker:
                try:
                    # This is where "Expecting value: line 1 column 1 (char 0)" often occurs
                    info = ticker.info
                    logger.info(f"Successfully got ticker info for {yahoo_symbol}")
                except Exception as info_error:
                    logger.warning(f"Ticker info failed for {yahoo_symbol}: {info_error}")
                    info = {}  # Continue with empty info

            stock_data = {
                "symbol": symbol.upper(),
                "name": stock_info.company_name,
                "exchange": stock_info.exchange,
                "currentPrice": current_price,
                "change": change,
                "changePercent": change_percent,
                "volume": int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                "marketCap": info.get('marketCap'),
                "pe": info.get('trailingPE'),
                "sector": stock_info.sector or info.get('sector', 'Unknown'),
                "high52Week": info.get('fiftyTwoWeekHigh'),
                "low52Week": info.get('fiftyTwoWeekLow'),
                "dividendYield": info.get('dividendYield'),
                "dayHigh": float(hist['High'].iloc[-1]),
                "dayLow": float(hist['Low'].iloc[-1]),
                "open": float(hist['Open'].iloc[-1])
            }

            return {
                "stock": sanitize_for_json(stock_data),
                "source": "yfinance",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Comprehensive error fetching quote for {symbol}: {str(e)}")
            return None

    def _is_market_open(self) -> bool:
        """Check if Indian market is open"""
        try:
            import pytz
            
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)

            # Weekend check
            if now.weekday() >= 5:
                return False

            # Market hours: 9:15 AM - 3:30 PM IST
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

            return market_open <= now <= market_close
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return False  # Default to closed if error

    def _get_period_dates(self, period: str):
        """Convert period string to start/end dates"""
        today = date.today()
        period_mapping = {
            '1D': timedelta(days=1),
            '1W': timedelta(weeks=1), 
            '15D': timedelta(days=15),
            '1M': timedelta(days=30),
            '6M': timedelta(days=180),
            '1Y': timedelta(days=365),
            '5Y': timedelta(days=365 * 5)
        }

        if period.upper() == 'ALL':
            return None, today

        delta = period_mapping.get(period.upper())
        if delta:
            return today - delta, today

        return today - timedelta(days=180), today  # Default 6M

    async def _fetch_and_store_history(self, yahoo_symbol: str, symbol: str, start_date: Optional[date] = None):
        """Fetch and store historical data"""
        try:
            ticker = yf.Ticker(yahoo_symbol)
            
            if start_date:
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
                hist = ticker.history(start=start_str, end=end_str)
            else:
                hist = ticker.history(period='max')

            if not hist.empty:
                await self._store_history_to_db(symbol, hist)
                logger.info(f"Fetched and stored history for {symbol}")
            else:
                logger.warning(f"No history data fetched for {yahoo_symbol}")

        except Exception as e:
            logger.error(f"Error fetching history for {yahoo_symbol}: {e}")

    async def _store_history_to_db(self, symbol: str, data: pd.DataFrame):
        """Store historical data to database"""
        try:
            # Prepare bulk insert data
            insert_data = []
            for timestamp, row in data.iterrows():
                insert_data.append({
                    'symbol': symbol.upper(),
                    'date': timestamp.date(),
                    'open': float(row['Open']) if not pd.isna(row['Open']) else None,
                    'high': float(row['High']) if not pd.isna(row['High']) else None,
                    'low': float(row['Low']) if not pd.isna(row['Low']) else None,
                    'close': float(row['Close']) if not pd.isna(row['Close']) else None,
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else None
                })

            # Bulk insert using raw SQL for performance
            if insert_data:
                query = text("""
                    INSERT INTO stock_history (symbol, date, open, high, low, close, volume, last_updated)
                    VALUES (:symbol, :date, :open, :high, :low, :close, :volume, NOW())
                    ON CONFLICT (symbol, date) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        last_updated = NOW()
                """)

                await self.db.execute(query, insert_data)
                await self.db.commit()
                logger.info(f"Stored {len(insert_data)} records for {symbol}")

        except Exception as e:
            logger.error(f"Error storing history for {symbol}: {e}")
            await self.db.rollback()

    async def _get_history_from_db(self, symbol: str, start_date: Optional[date], end_date: Optional[date]) -> List[Dict]:
        """Get historical data from database"""
        try:
            conditions = [StockHistory.symbol == symbol.upper()]
            
            if start_date:
                conditions.append(StockHistory.date >= start_date)
            if end_date:
                conditions.append(StockHistory.date <= end_date)

            stmt = select(StockHistory).where(and_(*conditions)).order_by(StockHistory.date.asc())
            result = await self.db.execute(stmt)
            rows = result.scalars().all()

            return [
                {
                    "timestamp": row.date.strftime('%Y-%m-%d'),
                    "open": float(row.open) if row.open is not None else 0,
                    "high": float(row.high) if row.high is not None else 0,
                    "low": float(row.low) if row.low is not None else 0,
                    "close": float(row.close) if row.close is not None else 0,
                    "volume": int(row.volume) if row.volume is not None else 0
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting history from DB for {symbol}: {e}")
            return []

    async def _get_latest_db_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest quote from database for off-market hours"""
        try:
            stmt = select(StockHistory).where(
                StockHistory.symbol == symbol.upper()
            ).order_by(StockHistory.date.desc()).limit(1)
            
            result = await self.db.execute(stmt)
            latest_row = result.scalar_one_or_none()

            if not latest_row:
                return None

            # Get stock info
            stmt = select(Stock).where(Stock.symbol == symbol.upper())
            result = await self.db.execute(stmt)
            stock_info = result.scalar_one_or_none()

            if not stock_info:
                return None

            return {
                "stock": {
                    "symbol": symbol.upper(),
                    "name": stock_info.company_name,
                    "exchange": stock_info.exchange,
                    "currentPrice": float(latest_row.close),
                    "change": 0.0,  # Can't calculate without previous day
                    "changePercent": 0.0,
                    "volume": int(latest_row.volume) if latest_row.volume else 0,
                    "dayHigh": float(latest_row.high),
                    "dayLow": float(latest_row.low),
                    "open": float(latest_row.open),
                    "sector": stock_info.sector
                },
                "source": "database",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting latest DB quote for {symbol}: {e}")
            return None
