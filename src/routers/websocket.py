from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from src.auth.token_manager import TokenManager
import json
from typing import Dict

router = APIRouter(prefix="/ws", tags=["Web Socket"])


def get_token_manager() -> TokenManager:
    return TokenManager()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_event(self, user_id: str, event: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(event))

    async def broadcast(self, event: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(event))


manager = ConnectionManager()


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, token: str = Depends(get_token_manager()._verify_token)
):
    user_id = token
    if not user_id:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            if event["type"] == "invitation":
                await manager.send_event(event["to"], event)
            elif event["type"] == "status":
                await manager.broadcast(event)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
