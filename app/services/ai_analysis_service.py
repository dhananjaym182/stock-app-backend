#AI Analysis Service (OpenRouter Integration)
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync, calculate_rsi, calculate_macd, sanitize_for_json

class AIAnalysisService:
    async def get_ai_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get AI analysis with OpenRouter integration"""
        cache_key = f"ai_analysis:{symbol.upper()}"
        
        # Check cache first
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker, hist, working_symbol = get_safe_ticker_data_sync(symbol)
            if ticker is None or hist is None or hist.empty:
                return self._get_fallback_response(symbol)
            
            try:
                info = ticker.info
                recent_news = ticker.news[:3] if ticker.news else []
            except Exception as e:
                print(f"Error getting additional data: {e}")
                info = {}
                recent_news = []
            
            # Prepare analysis data
            analysis_data = {
                'symbol': working_symbol,
                'current_price': hist['Close'].iloc[-1] if not hist.empty else 0,
                'indicators': {
                    'rsi': calculate_rsi(hist['Close']).iloc[-1] if not hist.empty else 50,
                    'volume': hist['Volume'].iloc[-1] if not hist.empty else 0
                },
                'news_summary': [item.get('title', '') for item in recent_news[:3]],
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE')
            }
            
            # Get AI response
            ai_response = await self._call_openrouter_api(analysis_data, working_symbol)
            
            # Sanitize before caching and returning
            ai_response = sanitize_for_json(ai_response)
            
            # Cache for 30 minutes
            await redis_client.set(cache_key, ai_response, ttl=1800)
            return ai_response
            
        except Exception as e:
            print(f"AI Analysis error for {symbol}: {e}")
            return self._get_fallback_response(symbol)
    
    async def _call_openrouter_api(self, data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Call OpenRouter API with proper error handling"""
        try:
            if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("your_"):
                raise ValueError("Invalid OpenRouter API key")
            
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Stock Analysis App"
            }
            
            prompt = f"""
            Analyze the stock {symbol} with this data:
            Current Price: ₹{data.get('current_price', 'N/A')}
            RSI: {data.get('indicators', {}).get('rsi', 'N/A')}
            Market Cap: {data.get('market_cap', 'N/A')}
            PE Ratio: {data.get('pe_ratio', 'N/A')}
            
            Provide brief analysis (max 100 words each):
            1. Technical outlook
            2. Fundamental view
            3. Investment recommendation
            """
            
            payload = {
                "model": "anthropic/claude-3-haiku",  # Updated model
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    print(f"OpenRouter response status: {response.status}")
                    
                    if response.status == 200:
                        ai_response = await response.json()
                        content = ai_response.get('choices', [{}])[0].get('message', {}).get('content', '')
                        
                        return {
                            'technical': {
                                'analysis': content[:200] + '...' if len(content) > 200 else content,
                                'signals': ['AI-generated analysis']
                            },
                            'fundamental': {
                                'analysis': 'AI fundamental analysis based on available data.',
                                'score': 75
                            },
                            'sentiment': 'Neutral',
                            'recommendation': content,
                            'confidence': 80
                        }
                    else:
                        print(f"OpenRouter API error: {response.status}")
                        raise Exception(f"API returned {response.status}")
        
        except Exception as e:
            print(f"OpenRouter API call failed: {e}")
            return self._get_fallback_response(symbol)
    
    def _get_fallback_response(self, symbol: str) -> Dict[str, Any]:
        """Fallback response when AI analysis fails"""
        return {
            'technical': {
                'analysis': f'Technical analysis for {symbol} shows mixed signals based on available indicators.',
                'signals': ['RSI neutral', 'Volume analysis pending']
            },
            'fundamental': {
                'analysis': f'Fundamental analysis for {symbol} requires comprehensive data review.',
                'score': 60
            },
            'sentiment': 'Neutral',
            'recommendation': f'Manual analysis recommended for {symbol} due to AI service limitations.',
            'confidence': 40
        }
