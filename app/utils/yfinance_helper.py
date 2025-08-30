import yfinance as yf
import pandas as pd
import asyncio
from datetime import datetime
import json
import math
from typing import Optional, Tuple, Dict, Any

# Index symbols that should not have any suffix
INDEX_SYMBOLS = {'^NSEI', '^NSEBANK', '^DJI', '^FTSE', '^BSESN'}

def sanitize_for_json(data):
    """Recursively sanitize data replacing NaN, Inf, and Timestamp with JSON-safe types"""
    if isinstance(data, dict):
        return {str(k): sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(i) for i in data]
    elif isinstance(data, pd.Series):
        return {str(k): sanitize_for_json(v) for k, v in data.to_dict().items()}
    elif isinstance(data, pd.DataFrame):
        return {str(idx): sanitize_for_json(row.to_dict()) for idx, row in data.iterrows()}
    elif isinstance(data, (float, pd.core.dtypes.generic.floating)):
        if math.isnan(data) or math.isinf(data):
            return None
        return float(data)
    elif isinstance(data, (int, pd.core.dtypes.generic.integer)):
        return int(data)
    elif isinstance(data, (datetime, pd.Timestamp)):
        return data.isoformat()
    elif pd.isna(data):
        return None
    else:
        return data

async def get_safe_ticker_data_async(symbol: str) -> Tuple[Optional[yf.Ticker], Optional[pd.DataFrame], Optional[str]]:
    """
    Async version of get_safe_ticker_data with proper symbol lookup priority
    """
    return await asyncio.get_event_loop().run_in_executor(
        None, get_safe_ticker_data_sync, symbol
    )

def get_safe_ticker_data_sync(symbol: str) -> Tuple[Optional[yf.Ticker], Optional[pd.DataFrame], Optional[str]]:
    """
    Safely get ticker data with proper symbol lookup priority:
    1. Index symbols (^NSEI, ^NSEBANK, ^DJI, ^FTSE, ^BSESN) - use as-is
    2. If symbol ends with .BSE → convert to .BO first, fallback .NS
    3. If plain symbol (no suffix) → try .NS first, then .BO
    4. If already .NS or .BO → use as-is
    """
    clean_symbol = symbol.lstrip("$").upper()
    
    if clean_symbol in INDEX_SYMBOLS:
        symbol_variations = [clean_symbol]
    elif clean_symbol.endswith(".BSE"):
        base = clean_symbol[:-4]  # remove .BSE
        symbol_variations = [f"{base}.BO", f"{base}.NS"]
    elif clean_symbol.endswith(".NS") or clean_symbol.endswith(".BO"):
        symbol_variations = [clean_symbol]
    else:
        symbol_variations = [f"{clean_symbol}.NS", f"{clean_symbol}.BO"]
    
    for variant in symbol_variations:
        try:
            ticker = yf.Ticker(variant)
            hist = ticker.history(period="6mo")
            if not hist.empty:
                return ticker, hist, variant
        except Exception as e:
            print(f"Error with symbol {variant}: {e}")
            continue
    
    return None, None, None

def calculate_rsi(prices, window=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    exp1 = prices.ewm(span=fast).mean()
    exp2 = prices.ewm(span=slow).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

def calculate_technical_recommendations(hist: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """Calculate technical indicators and generate recommendations with NaN handling"""
    try:
        close_prices = hist['Close']
        volume = hist['Volume']
        
        # Calculate moving averages with NaN checks
        ma_20 = close_prices.rolling(window=20).mean().iloc[-1]
        ma_50 = close_prices.rolling(window=50).mean().iloc[-1]
        ma_200 = close_prices.rolling(window=200).mean().iloc[-1]
        current_price = close_prices.iloc[-1]
        
        # Calculate RSI with NaN handling
        rsi = calculate_rsi(close_prices).iloc[-1]
        
        # Calculate MACD with NaN handling
        macd_line, signal_line = calculate_macd(close_prices)
        macd_current = macd_line.iloc[-1]
        signal_current = signal_line.iloc[-1]
        
        # Safe value function to handle NaN/Inf values
        def safe_value(val, default=0):
            try:
                if pd.isna(val) or math.isnan(val) or math.isinf(val):
                    return default
                return float(val)
            except:
                return default
        
        # Safe comparison function
        def safe_compare(val1, val2, default=False):
            try:
                if pd.isna(val1) or pd.isna(val2):
                    return default
                return val1 > val2
            except:
                return default
        
        buy_signals = 0
        sell_signals = 0
        
        # Moving average signals with safe comparisons
        if (safe_compare(current_price, ma_20) and
            safe_compare(ma_20, ma_50) and
            safe_compare(ma_50, ma_200)):
            buy_signals += 2
        elif (safe_compare(ma_20, current_price) and
              safe_compare(ma_50, ma_20) and
              safe_compare(ma_200, ma_50)):
            sell_signals += 2
        
        # RSI signals with safe checks
        rsi_val = safe_value(rsi, 50)
        if rsi_val < 30:
            buy_signals += 1
        elif rsi_val > 70:
            sell_signals += 1
        
        # MACD signals with safe checks
        if safe_compare(macd_current, signal_current):
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Generate recommendation
        if buy_signals > sell_signals:
            rating = "Strong Buy" if buy_signals - sell_signals >= 2 else "Buy"
        elif sell_signals > buy_signals:
            rating = "Strong Sell" if sell_signals - buy_signals >= 2 else "Sell"
        else:
            rating = "Hold"
        
        # Calculate target price with safe values
        current_price_safe = safe_value(current_price, 100)
        target_price = current_price_safe * (1.1 if buy_signals > sell_signals else 0.95)
        
        return sanitize_for_json({
            'rating': rating,
            'targetPrice': round(target_price, 2),
            'currentPrice': round(current_price_safe, 2),
            'upside': round(((target_price - current_price_safe) / current_price_safe) * 100, 2),
            'analystCount': 1,
            'buyCount': buy_signals,
            'holdCount': 1,
            'sellCount': sell_signals,
            'averageRating': (buy_signals * 5 + sell_signals * 1) / max(buy_signals + sell_signals, 1),
            'summary': f"Based on technical analysis, {symbol} shows {rating.lower()} signals.",
            'keyPoints': [
                f"Current price: ₹{current_price_safe:.2f}",
                f"RSI: {rsi_val:.2f} ({'Oversold' if rsi_val < 30 else 'Overbought' if rsi_val > 70 else 'Normal'})",
                f"Price vs MA20: {'Above' if safe_compare(current_price, ma_20) else 'Below'}",
                f"MACD: {'Bullish' if safe_compare(macd_current, signal_current) else 'Bearish'}",
                f"Volume trend: {'High' if safe_compare(volume.iloc[-1], volume.rolling(20).mean().iloc[-1]) else 'Normal'}"
            ],
            'indicators': {
                'rsi': safe_value(rsi, 50),
                'ma20': safe_value(ma_20, current_price_safe),
                'ma50': safe_value(ma_50, current_price_safe),
                'ma200': safe_value(ma_200, current_price_safe),
                'macd': safe_value(macd_current, 0),
                'signal': safe_value(signal_current, 0)
            }
        })
        
    except Exception as e:
        return {'error': f'Failed to calculate recommendations: {str(e)}'}
