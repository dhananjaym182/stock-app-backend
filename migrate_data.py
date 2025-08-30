#!/usr/bin/env python3
"""
Simple stocks-only migration from MySQL to PostgreSQL
"""
import asyncio
import mysql.connector
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.database import Base
from datetime import datetime

# Database configurations
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'jay',
    'database': 'indian_stocks_db'
}

POSTGRES_ASYNC_URL = "postgresql+asyncpg://postgres:jay@localhost/indian_stocks_db"

async def migrate_stocks_only():
    """Migrate only stocks table with all columns"""
    print("🚀 Starting Stocks-Only Migration")
    print("=" * 50)
    
    # Connect to databases
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    async_engine = create_async_engine(POSTGRES_ASYNC_URL)
    
    try:
        # Recreate PostgreSQL tables with updated schema
        print("🏗️ Recreating PostgreSQL tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables recreated with updated schema")
        
        # Get MySQL stocks data with ALL columns
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, symbol, yahoo_symbol, company_name, sector, industry, 
                   exchange, sectorid, is_active, created_at, updated_at
            FROM stocks 
            WHERE is_active = 1
        """)
        
        mysql_stocks = cursor.fetchall()
        cursor.close()
        
        print(f"📊 Found {len(mysql_stocks)} active stocks in MySQL")
        
        # Insert into PostgreSQL with proper column mapping
        migrated_count = 0
        errors = []
        
        async with async_engine.begin() as conn:
            for stock in mysql_stocks:
                try:
                    # Map all columns from MySQL to PostgreSQL
                    clean_stock = {
                        'symbol': stock['symbol'],
                        'yahoo_symbol': stock['yahoo_symbol'],
                        'company_name': stock['company_name'] or '',
                        'sector': stock['sector'],
                        'industry': stock['industry'],  # Include industry
                        'exchange': stock['exchange'] or 'BSE',
                        'sectorid': stock['sectorid'],  # Include sectorid
                        'is_active': bool(stock['is_active']),
                        'created_at': stock.get('created_at') or datetime.now(),
                        'updated_at': stock.get('updated_at') or datetime.now()
                    }
                    
                    await conn.execute(text("""
                        INSERT INTO stocks (symbol, yahoo_symbol, company_name, sector, industry, 
                                          exchange, sectorid, is_active, created_at, updated_at)
                        VALUES (:symbol, :yahoo_symbol, :company_name, :sector, :industry, 
                                :exchange, :sectorid, :is_active, :created_at, :updated_at)
                        ON CONFLICT (symbol) DO UPDATE SET
                            yahoo_symbol = EXCLUDED.yahoo_symbol,
                            company_name = EXCLUDED.company_name,
                            sector = EXCLUDED.sector,
                            industry = EXCLUDED.industry,
                            exchange = EXCLUDED.exchange,
                            sectorid = EXCLUDED.sectorid,
                            is_active = EXCLUDED.is_active,
                            updated_at = EXCLUDED.updated_at
                    """), clean_stock)
                    
                    migrated_count += 1
                    
                    # Progress indicator
                    if migrated_count % 1000 == 0:
                        print(f"📈 Migrated {migrated_count} stocks...")
                    
                except Exception as e:
                    error_msg = f"Error migrating {stock.get('symbol', 'UNKNOWN')}: {e}"
                    errors.append(error_msg)
        
        # Validation
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM stocks"))
            pg_count = result.fetchone()[0]
            
            # Sample data
            result = await conn.execute(text("""
                SELECT symbol, company_name, sector, industry, exchange, sectorid 
                FROM stocks LIMIT 5
            """))
            samples = result.fetchall()
        
        # Results
        print(f"\n🎯 Migration Results:")
        print(f"   MySQL stocks: {len(mysql_stocks)}")
        print(f"   PostgreSQL stocks: {pg_count}")
        print(f"   Successfully migrated: {migrated_count}")
        print(f"   Errors: {len(errors)}")
        
        if samples:
            print(f"\n📋 Sample migrated data:")
            for sample in samples:
                print(f"   {sample[0]}: {sample[1]} ({sample[2]}, {sample[4]})")
        
        if len(errors) > 0:
            print(f"\n❌ First few errors:")
            for error in errors[:5]:
                print(f"   - {error}")
        
        success = migrated_count >= len(mysql_stocks) * 0.95
        
        if success:
            print(f"\n✅ Stocks migration completed successfully!")
            print(f"📊 Stock history will be populated by the API as needed")
            return True
        else:
            print(f"\n⚠️ Migration completed with issues")
            return False
    
    finally:
        mysql_conn.close()
        await async_engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(migrate_stocks_only())
    
    if success:
        print(f"\n🎉 Next Steps:")
        print(f"1. Start Redis: redis-server")
        print(f"2. Start API: python main.py")
        print(f"3. Test: http://localhost:8000/api/quote/RELIANCE")
        print(f"4. Stop MySQL: sudo systemctl stop mysql")
    
    exit(0 if success else 1)
