from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.websocket_service import websocket_manager
import json
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time stock data"""
    client_id = str(uuid.uuid4())
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "client_id": client_id,
            "message": "WebSocket connected successfully"
        }))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "subscribe":
                symbols = message.get("symbols", [])
                await websocket_manager.subscribe_symbols(client_id, symbols)
                
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "symbols": symbols,
                    "client_id": client_id
                }))
            
            elif message_type == "unsubscribe":
                symbols = message.get("symbols", [])
                for symbol in symbols:
                    websocket_manager.unsubscribe_symbol(client_id, symbol)
                
                await websocket.send_text(json.dumps({
                    "type": "unsubscribed",
                    "symbols": symbols,
                    "client_id": client_id
                }))
            
            elif message_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        websocket_manager.disconnect(client_id)

@router.get("/stream/status")
async def get_websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": len(websocket_manager.active_connections),
        "total_subscriptions": sum(len(subs) for subs in websocket_manager.subscriptions.values()),
        "active_symbols": list(websocket_manager.symbol_subscribers.keys()),
        "update_tasks": len(websocket_manager.update_tasks)
    }
