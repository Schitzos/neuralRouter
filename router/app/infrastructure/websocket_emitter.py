"""
WebSocket event emitter implementation
"""
import json
import asyncio
from typing import List, Set
from fastapi import WebSocket
from ..domain.interfaces.event_emitter import IEventEmitter
from ..domain.entities import RouterEvent


class WebSocketEmitter(IEventEmitter):
    """WebSocket-based event emitter for real-time events"""
    
    def __init__(self):
        self.connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Add a new WebSocket connection"""
        await websocket.accept()
        self.connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.connections.discard(websocket)
    
    async def emit(self, event: RouterEvent) -> None:
        """Emit event to all connected WebSocket clients"""
        if not self.connections:
            return
            
        # Convert event to JSON
        event_data = {
            "id": event.id,
            "session_id": event.session_id,
            "request_id": event.request_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data
        }
        
        message = json.dumps(event_data)
        
        # Send to all connections (remove failed ones)
        disconnected = set()
        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        self.connections -= disconnected