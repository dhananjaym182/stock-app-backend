from app.core.redis_client import redis_client
from typing import Dict, Any, Optional, List
import asyncio

class CacheAdminService:
    async def clear_cache(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """Clear cache entries using SCAN for better performance"""
        try:
            if not redis_client.redis:
                return {"error": "Redis not connected", "deleted_count": 0}
            
            deleted_count = 0
            
            if prefix:
                # Use SCAN to find and delete keys with prefix (safe for large datasets)
                pattern = f"*{prefix}*"
                deleted_count = await self._delete_keys_by_pattern(pattern)
            else:
                # Clear all keys in current database
                await redis_client.redis.flushdb()
                deleted_count = -1  # Indicates full flush
            
            return {
                "message": f"Cache cleared successfully",
                "deleted_count": deleted_count,
                "prefix": prefix or "all",
                "method": "scan_delete" if prefix else "flushdb"
            }
            
        except Exception as e:
            return {
                "error": f"Cache clear failed: {str(e)}", 
                "deleted_count": 0,
                "details": str(e)
            }
    
    async def _delete_keys_by_pattern(self, pattern: str) -> int:
        """Delete keys by pattern using SCAN (non-blocking)"""
        deleted_count = 0
        cursor = 0
        batch_size = 1000  # Process in batches
        
        try:
            while True:
                # Use SCAN instead of KEYS for better performance
                cursor, keys = await redis_client.redis.scan(
                    cursor=cursor, 
                    match=pattern, 
                    count=batch_size
                )
                
                if keys:
                    # Delete keys in pipeline for better performance
                    pipe = redis_client.redis.pipeline()
                    for key in keys:
                        pipe.delete(key)
                    await pipe.execute()
                    deleted_count += len(keys)
                
                # Break when cursor returns to 0 (full scan complete)
                if cursor == 0:
                    break
                    
        except Exception as e:
            print(f"Error in pattern deletion: {e}")
            raise e
        
        return deleted_count
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            if not redis_client.redis:
                return {"error": "Redis not connected"}
            
            # Get Redis info
            info = await redis_client.redis.info()
            
            # Get database info
            db_info = await redis_client.redis.info('keyspace')
            
            # Count total keys more efficiently
            total_keys = 0
            try:
                # Try to get key count from keyspace info first
                if 'db0' in db_info:
                    db0_info = db_info['db0']
                    if isinstance(db0_info, dict) and 'keys' in db0_info:
                        total_keys = db0_info['keys']
                    elif isinstance(db0_info, str):
                        # Parse string format: keys=123,expires=45,avg_ttl=678
                        for part in db0_info.split(','):
                            if part.startswith('keys='):
                                total_keys = int(part.split('=')[1])
                                break
                else:
                    # Fallback: count using DBSIZE (fast)
                    total_keys = await redis_client.redis.dbsize()
            except:
                total_keys = 0
            
            # Calculate hit rate safely
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total_requests = hits + misses
            hit_rate = round((hits / max(1, total_requests)) * 100, 2)
            
            return {
                "status": "connected",
                "redis_version": info.get('redis_version', 'Unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "used_memory_human": info.get('used_memory_human', 'Unknown'),
                "used_memory_peak_human": info.get('used_memory_peak_human', 'Unknown'),
                "total_keys": total_keys,
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": hits,
                "keyspace_misses": misses,
                "hit_rate_percentage": hit_rate,
                "uptime_in_seconds": info.get('uptime_in_seconds', 0),
                "uptime_in_days": round(info.get('uptime_in_seconds', 0) / 86400, 1),
                "redis_mode": info.get('redis_mode', 'standalone'),
                "cache_performance": {
                    "excellent": hit_rate >= 90,
                    "good": 70 <= hit_rate < 90,
                    "needs_improvement": hit_rate < 70
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get cache stats: {str(e)}"}
    
    async def get_cache_keys(self, pattern: str = "*", limit: int = 100) -> Dict[str, Any]:
        """Get cache keys using SCAN for better performance"""
        try:
            if not redis_client.redis:
                return {"error": "Redis not connected", "keys": []}
            
            keys = []
            cursor = 0
            scanned_count = 0
            
            while len(keys) < limit:
                cursor, batch_keys = await redis_client.redis.scan(
                    cursor=cursor, 
                    match=pattern, 
                    count=min(100, limit - len(keys))
                )
                
                keys.extend(batch_keys)
                scanned_count += len(batch_keys)
                
                if cursor == 0:  # Full scan complete
                    break
            
            # Limit results
            limited_keys = keys[:limit]
            
            return {
                "keys": limited_keys,
                "total_found": len(keys),
                "shown": len(limited_keys),
                "pattern": pattern,
                "scan_complete": cursor == 0
            }
            
        except Exception as e:
            return {"error": f"Failed to get cache keys: {str(e)}", "keys": []}
    
    async def delete_cache_key(self, key: str) -> Dict[str, Any]:
        """Delete a specific cache key"""
        try:
            if not redis_client.redis:
                return {"error": "Redis not connected", "deleted": False}
            
            deleted = await redis_client.redis.delete(key)
            
            return {
                "key": key,
                "deleted": bool(deleted),
                "message": f"Key {'deleted successfully' if deleted else 'not found or already deleted'}"
            }
            
        except Exception as e:
            return {"error": f"Failed to delete cache key: {str(e)}", "deleted": False}
    
    async def get_cache_key_info(self, key: str) -> Dict[str, Any]:
        """Get information about a specific cache key"""
        try:
            if not redis_client.redis:
                return {"error": "Redis not connected"}
            
            exists = await redis_client.redis.exists(key)
            if not exists:
                return {"error": "Key not found", "key": key}
            
            # Get key info
            key_type = await redis_client.redis.type(key)
            ttl = await redis_client.redis.ttl(key)
            
            info = {
                "key": key,
                "exists": True,
                "type": key_type,
                "ttl_seconds": ttl,
                "ttl_human": self._format_ttl(ttl)
            }
            
            # Get value size (approximate)
            try:
                memory_usage = await redis_client.redis.memory_usage(key)
                info["memory_usage_bytes"] = memory_usage
                info["memory_usage_human"] = self._format_bytes(memory_usage)
            except:
                info["memory_usage_bytes"] = "Unknown"
                info["memory_usage_human"] = "Unknown"
            
            return info
            
        except Exception as e:
            return {"error": f"Failed to get key info: {str(e)}"}
    
    def _format_ttl(self, ttl_seconds: int) -> str:
        """Format TTL in human readable format"""
        if ttl_seconds == -1:
            return "No expiration"
        elif ttl_seconds == -2:
            return "Key does not exist"
        elif ttl_seconds < 60:
            return f"{ttl_seconds} seconds"
        elif ttl_seconds < 3600:
            return f"{ttl_seconds // 60} minutes"
        elif ttl_seconds < 86400:
            return f"{ttl_seconds // 3600} hours"
        else:
            return f"{ttl_seconds // 86400} days"
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"
    
    async def clear_cache_by_prefix_list(self, prefixes: List[str]) -> Dict[str, Any]:
        """Clear cache for multiple prefixes efficiently"""
        try:
            if not redis_client.redis:
                return {"error": "Redis not connected", "results": []}
            
            results = []
            total_deleted = 0
            
            for prefix in prefixes:
                pattern = f"*{prefix}*"
                deleted_count = await self._delete_keys_by_pattern(pattern)
                results.append({
                    "prefix": prefix,
                    "deleted_count": deleted_count,
                    "pattern": pattern
                })
                total_deleted += deleted_count
            
            return {
                "message": "Multiple prefix cache clear completed",
                "total_deleted": total_deleted,
                "results": results
            }
            
        except Exception as e:
            return {"error": f"Failed to clear multiple prefixes: {str(e)}", "results": []}
