from fastapi import APIRouter, HTTPException, Query
from app.services.cache_admin_service import CacheAdminService
from typing import Optional, List

router = APIRouter()

@router.post("/cache/clear")
async def clear_cache(prefix: Optional[str] = Query(None, description="Cache key prefix to clear (e.g., 'quote', 'history')")):
    """Clear cache entries - improved version with SCAN"""
    cache_service = CacheAdminService()
    result = await cache_service.clear_cache(prefix)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/cache/clear-multiple")
async def clear_multiple_prefixes(prefixes: List[str]):
    """Clear cache for multiple prefixes efficiently"""
    if not prefixes:
        raise HTTPException(status_code=400, detail="At least one prefix is required")
    
    cache_service = CacheAdminService()
    result = await cache_service.clear_cache_by_prefix_list(prefixes)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/cache/stats")
async def get_cache_stats():
    """Get comprehensive cache statistics"""
    cache_service = CacheAdminService()
    result = await cache_service.get_cache_stats()
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/cache/keys")
async def get_cache_keys(
    pattern: str = Query(default="*", description="Pattern to match keys (e.g., 'quote:*', 'history:*')"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of keys to return")
):
    """Get cache keys using efficient SCAN method"""
    cache_service = CacheAdminService()
    result = await cache_service.get_cache_keys(pattern, limit)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/cache/key/{key}/info")
async def get_cache_key_info(key: str):
    """Get detailed information about a specific cache key"""
    cache_service = CacheAdminService()
    result = await cache_service.get_cache_key_info(key)
    
    if "error" in result:
        raise HTTPException(status_code=404 if "not found" in result["error"].lower() else 500, detail=result["error"])
    
    return result

@router.delete("/cache/key/{key}")
async def delete_cache_key(key: str):
    """Delete a specific cache key"""
    cache_service = CacheAdminService()
    result = await cache_service.delete_cache_key(key)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/cache/cleanup")
async def cleanup_expired_cache():
    """Clean expired cache entries - Redis handles TTL automatically"""
    cache_service = CacheAdminService()
    stats = await cache_service.get_cache_stats()
    
    return {
        "message": "Redis automatically handles TTL expiration",
        "cache_status": stats.get("status", "unknown"),
        "total_keys": stats.get("total_keys", 0),
        "hit_rate": f"{stats.get('hit_rate_percentage', 0)}%",
        "memory_usage": stats.get("used_memory_human", "Unknown"),
        "action": "automatic_cleanup_active"
    }

# Additional utility endpoints
@router.get("/cache/health")
async def cache_health_check():
    """Quick cache health check"""
    cache_service = CacheAdminService()
    stats = await cache_service.get_cache_stats()
    
    if "error" in stats:
        raise HTTPException(status_code=503, detail="Cache unavailable")
    
    return {
        "status": "healthy",
        "redis_connected": True,
        "total_keys": stats.get("total_keys", 0),
        "hit_rate": f"{stats.get('hit_rate_percentage', 0)}%",
        "uptime_days": stats.get("uptime_in_days", 0)
    }
