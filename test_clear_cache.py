# Test in your FastAPI app
import asyncio
from app.services.cache_admin_service import CacheAdminService

async def test_cache_clear():
    service = CacheAdminService()
    
    # Test clearing by prefix
    result = await service.clear_cache("quote")
    print(f"Cleared quote cache: {result}")
    
    # Test getting stats
    stats = await service.get_cache_stats()
    print(f"Cache stats: {stats}")

# Run the test
asyncio.run(test_cache_clear())
