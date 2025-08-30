# Clear all cache
POST /api/cache/clear

# Clear specific prefix (e.g., all quote cache)
POST /api/cache/clear?prefix=quote

# Clear multiple prefixes
POST /api/cache/clear-multiple
Body: ["quote", "history", "search"]

# Get cache statistics
GET /api/cache/stats

# Get keys with pattern
GET /api/cache/keys?pattern=quote:*&limit=50

# Get info about specific key
GET /api/cache/key/quote:RELIANCE/info

# Delete specific key
DELETE /api/cache/key/quote:RELIANCE

# Health check
GET /api/cache/health
