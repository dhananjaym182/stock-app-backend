#!/usr/bin/env python3
"""
Final setup script after migration
"""
import asyncio
from app.core.database import engine
from app.core.redis_client import redis_client
from sqlalchemy import text

async def test_postgresql_connection():
    """Test PostgreSQL connection and data"""
    try:
        async with engine.begin() as conn:
            # Test basic connection
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connected: {version}")
            
            # Check migrated data
            result = await conn.execute(text("SELECT COUNT(*) FROM stocks"))
            stocks_count = result.fetchone()[0]
            print(f"✅ Stocks in database: {stocks_count}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM stock_history"))
            history_count = result.fetchone()[0]
            print(f"✅ History records in database: {history_count}")
            
            # Sample stock data
            if stocks_count > 0:
                result = await conn.execute(text("SELECT symbol, company_name FROM stocks LIMIT 3"))
                samples = result.fetchall()
                print("✅ Sample stocks:")
                for sample in samples:
                    print(f"   - {sample[0]}: {sample[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        return False

async def test_redis_connection():
    """Test Redis connection"""
    try:
        await redis_client.connect()
        await redis_client.set("test_key", {"test": "data"}, ttl=60)
        test_data = await redis_client.get("test_key")
        
        if test_data and test_data.get("test") == "data":
            print("✅ Redis connected and working")
            await redis_client.delete("test_key")
            return True
        else:
            print("❌ Redis test data mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

async def main():
    print("🧪 Testing Post-Migration Setup...")
    
    pg_ok = await test_postgresql_connection()
    redis_ok = await test_redis_connection()
    
    if pg_ok and redis_ok:
        print("\n🎉 All systems ready!")
        print("\nYou can now:")
        print("1. Start the FastAPI application: python main.py")
        print("2. Test API: http://localhost:8000/docs")
        print("3. Stop MySQL service (see commands below)")
        
        print("\n🛑 To stop MySQL service:")
        print("   Linux/Mac: sudo systemctl stop mysql && sudo systemctl disable mysql")
        print("   Windows: Stop 'MySQL' service from Services panel")
        
        return True
    else:
        print("\n❌ Setup incomplete - fix errors before proceeding")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
