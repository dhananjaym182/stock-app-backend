from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, BigInteger, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    yahoo_symbol = Column(String(30), index=True)
    company_name = Column(Text)
    sector = Column(String(100))
    industry = Column(String(100))  # Added missing column
    exchange = Column(String(20))
    sectorid = Column(String(50))   # Added missing column
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class StockHistory(Base):
    __tablename__ = "stock_history"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
        # Add unique constraint for ON CONFLICT to work
        Index('idx_symbol_date_unique', 'symbol', 'date', unique=True),
    )

# Keep other models the same...
class CompanyInfo(Base):
    __tablename__ = "company_info"
    
    symbol = Column(String(20), primary_key=True)
    data = Column(JSONB)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FinancialStatements(Base):
    __tablename__ = "financial_statements"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    statement_type = Column(String(20))
    period_type = Column(String(10))
    fiscal_period = Column(String(10))
    data = Column(JSONB)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class StockCache(Base):
    __tablename__ = "stock_cache"
    
    cache_key = Column(String(255), primary_key=True)
    data = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
