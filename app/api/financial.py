from fastapi import APIRouter, HTTPException
from app.services.financial_service import FinancialService

router = APIRouter()

@router.get("/financial/{symbol}/income_statement")
async def get_income_statement(symbol: str):
    """Get annual income statement"""
    financial_service = FinancialService()
    result = await financial_service.get_income_statement(symbol, quarterly=False)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result

@router.get("/financial/{symbol}/quarterly_income_statement")
async def get_quarterly_income_statement(symbol: str):
    """Get quarterly income statement"""
    financial_service = FinancialService()
    result = await financial_service.get_income_statement(symbol, quarterly=True)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result

@router.get("/financial/{symbol}/balance_sheet")
async def get_balance_sheet(symbol: str):
    """Get annual balance sheet"""
    financial_service = FinancialService()
    result = await financial_service.get_balance_sheet(symbol, quarterly=False)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result

@router.get("/financial/{symbol}/quarterly_balance_sheet")
async def get_quarterly_balance_sheet(symbol: str):
    """Get quarterly balance sheet"""
    financial_service = FinancialService()
    result = await financial_service.get_balance_sheet(symbol, quarterly=True)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result

@router.get("/financial/{symbol}/cashflow")
async def get_cashflow(symbol: str):
    """Get annual cash flow statement"""
    financial_service = FinancialService()
    result = await financial_service.get_cashflow(symbol, quarterly=False)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result

@router.get("/financial/{symbol}/quarterly_cashflow")
async def get_quarterly_cashflow(symbol: str):
    """Get quarterly cash flow statement"""
    financial_service = FinancialService()
    result = await financial_service.get_cashflow(symbol, quarterly=True)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result

# Backward compatibility with your existing Flask endpoint
@router.get("/financials/{symbol}")
async def get_financials_legacy(symbol: str):
    """Get comprehensive financials - backward compatible with Flask API"""
    financial_service = FinancialService()
    result = await financial_service.get_financials(symbol)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    
    return result
