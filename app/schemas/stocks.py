from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockQuoteResponse(BaseModel):
    symbol: str
    name: str
    exchange: str
    currentPrice: float
    change: float
    changePercent: float
    volume: int
    marketCap: Optional[int] = None
    pe: Optional[float] = None
    sector: Optional[str] = None
    high52Week: Optional[float] = None
    low52Week: Optional[float] = None
    dividendYield: Optional[float] = None
    dayHigh: float
    dayLow: float
    open: float

class StockQuoteResponseWrapper(BaseModel):
    stock: StockQuoteResponse
    source: str = "yfinance"
    timestamp: str

class HistoryDataPoint(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockHistoryResponse(BaseModel):
    data: List[HistoryDataPoint]
    source: str = "database+yfinance"
    timestamp: str
    period: str
    records: int

class SearchResult(BaseModel):
    symbol: str
    yahoo_symbol: str
    company_name: str
    exchange: str
    sector: Optional[str] = None

class SearchResponse(BaseModel):
    stocks: List[SearchResult]
    source: str = "database"
    total_results: int

class TechnicalIndicators(BaseModel):
    rsi: Optional[float] = None
    ma20: Optional[float] = None
    ma50: Optional[float] = None
    ma200: Optional[float] = None
    macd: Optional[float] = None
    signal: Optional[float] = None

class RecommendationResponse(BaseModel):
    rating: str
    targetPrice: float
    currentPrice: float
    upside: float
    analystCount: int
    buyCount: int
    holdCount: int
    sellCount: int
    averageRating: float
    summary: str
    keyPoints: List[str]
    indicators: TechnicalIndicators

class ErrorResponse(BaseModel):
    error: str
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
