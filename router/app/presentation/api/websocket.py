"""
WebSocket API endpoint for real-time events
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...infrastructure.websocket_emitter import WebSocketEmitter


def create_websocket_router(websocket_emitter: WebSocketEmitter) -> APIRouter:
    """Create WebSocket router"""
    router = APIRouter()
    
    @router.websocket("/ws/events")
    async def websocket_events(websocket: WebSocket):
        """WebSocket endpoint for real-time events"""
        await websocket_emitter.connect(websocket)
        try:
            # Keep connection alive
            while True:
                # Wait for client messages (ping/pong)
                await websocket.receive_text()
        except WebSocketDisconnect:
            websocket_emitter.disconnect(websocket)
    
    return router