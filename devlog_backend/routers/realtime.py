from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/realtime", tags=["realtime"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    # PUBLIC_INTERFACE
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    # PUBLIC_INTERFACE
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    # PUBLIC_INTERFACE
    async def broadcast(self, message: str):
        for conn in self.active_connections:
            await conn.send_text(message)

manager = ConnectionManager()

# PUBLIC_INTERFACE
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket real-time endpoint for comment notifications and live updates.
    Connect and receive updates on new comments, reactions, etc.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/help", tags=["realtime"])
async def get_ws_usage():
    """
    Returns usage instructions for the WebSocket endpoint.
    """
    return {
        "websocket_url": "/realtime/ws",
        "notes": "Connect via WebSocket to receive notifications about comments, reactions, live updates."
    }
