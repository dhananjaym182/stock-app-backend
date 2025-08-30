from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional, Any
import asyncio
import json
import yfinance as yf
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, asdict
from app.core.redis_client import redis_client
from app.utils.yfinance_helper import get_safe_ticker_data_sync
import logging

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # client_id -> symbols
        self.symbol_subscribers: Dict[str, Set[str]] = {}  # symbol -> client_ids
        self.update_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Handle client disconnection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.subscriptions:
            # Unsubscribe from all symbols
            for symbol in self.subscriptions[client_id].copy():
                self.unsubscribe_symbol(client_id, symbol)
            del self.subscriptions[client_id]
        
        logger.info(f"Client {client_id} disconnected")
    
    async def subscribe_symbols(self, client_id: str, symbols: list):
        """Subscribe client to symbols"""
        if client_id not in self.subscriptions:
            return
        
        for symbol in symbols:
            symbol = symbol.upper().strip()
            if symbol:
                self.subscriptions[client_id].add(symbol)
                
                if symbol not in self.symbol_subscribers:
                    self.symbol_subscribers[symbol] = set()
                self.symbol_subscribers[symbol].add(client_id)
                
                # Start update task if first subscriber
                if len(self.symbol_subscribers[symbol]) == 1:
                    self.update_tasks[symbol] = asyncio.create_task(
                        self._update_symbol_loop(symbol)
                    )
        
        # Send immediate cached data
        for symbol in symbols:
            cached_data = await redis_client.get(f"realtime:{symbol.upper()}")
            if cached_data:
                await self.send_to_client(client_id, {
                    "type": "stock_update",
                    "data": cached_data
                })
    
    def unsubscribe_symbol(self, client_id: str, symbol: str):
        """Unsubscribe client from symbol"""
        symbol = symbol.upper()
        
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(symbol)
        
        if symbol in self.symbol_subscribers:
            self.symbol_subscribers[symbol].discard(client_id)
            
            # Stop update task if no more subscribers
            if not self.symbol_subscribers[symbol]:
                if symbol in self.update_tasks:
                    self.update_tasks[symbol].cancel()
                    del self.update_tasks[symbol]
                del self.symbol_subscribers[symbol]
    
    async def send_to_client(self, client_id: str, message: dict):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                self.disconnect(client_id)
                return False
        return False
    
    async def broadcast_to_symbol_subscribers(self, symbol: str, data: dict):
        """Broadcast data to all subscribers of a symbol"""
        if symbol in self.symbol_subscribers:
            message = {"type": "stock_update", "data": data}
            disconnected_clients = []
            
            for client_id in self.symbol_subscribers[symbol].copy():
                success = await self.send_to_client(client_id, message)
                if not success:
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                self.unsubscribe_symbol(client_id, symbol)
    
    async def _update_symbol_loop(self, symbol: str):
        """Background task to fetch and broadcast symbol data"""
        while symbol in self.symbol_subscribers and self.symbol_subscribers[symbol]:
            try:
                # Fetch fresh data
                ticker, hist, working_symbol = get_safe_ticker_data_sync(symbol)
                
                if ticker and hist is not None and not hist.empty:
                    info = getattr(ticker, 'info', {})
                    latest = hist.iloc[-1]
                    prev_close = info.get('previousClose', latest['Close'])
                    
                    stock_data = StockData(
                        symbol=symbol,
                        price=float(latest['Close']),
                        change=float(latest['Close'] - prev_close),
                        change_percent=float((latest['Close'] - prev_close) / prev_close * 100),
                        volume=int(latest['Volume']),
                        timestamp=datetime.now().isoformat()
                    )
                    
                    data_dict = asdict(stock_data)
                    
                    # Cache for 30 seconds
                    await redis_client.set(f"realtime:{symbol}", data_dict, ttl=30)
                    
                    # Broadcast to subscribers
                    await self.broadcast_to_symbol_subscribers(symbol, data_dict)
                
                # Wait 5 seconds before next update
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating symbol {symbol}: {e}")
                await asyncio.sleep(10)  # Wait longer on error

# Global WebSocket manager
websocket_manager = WebSocketManager()
