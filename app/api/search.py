from fastapi import APIRouter, HTTPException, Query
from app.services.search_service import SearchService

router = APIRouter()

@router.get("/search_new/search")
async def search_symbols(
    q: str = Query(..., min_length=1, description="Search query"),
    max_results: int = Query(default=10, description="Maximum results to return"),
    news_count: int = Query(default=5, description="Number of news items to include"),
    include_research: bool = Query(default=False, description="Include research data")
):
    """Search for stocks and news"""
    search_service = SearchService()
    result = await search_service.search_symbols(q, max_results, news_count, include_research)
    
    if result is None:
        raise HTTPException(status_code=500, detail='Search failed')
    
    return result

@router.get("/search_new/lookup")
async def lookup_ticker(
    q: str = Query(..., min_length=1, description="Lookup query"),
    type: str = Query(default="all", description="Lookup type"),
    count: int = Query(default=10, description="Number of results")
):
    """Lookup ticker information"""
    valid_types = ['all', 'stock', 'etf', 'mutualfund', 'index', 'future', 'currency', 'cryptocurrency']
    if type not in valid_types:
        raise HTTPException(status_code=400, detail='Invalid lookup type')
    
    search_service = SearchService()
    result = await search_service.lookup_ticker(q, type, count)
    
    if result is None:
        raise HTTPException(status_code=500, detail='Lookup failed')
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/search_new/lookup/types")
async def get_lookup_types():
    """Get available lookup types"""
    search_service = SearchService()
    return search_service.get_lookup_types()
