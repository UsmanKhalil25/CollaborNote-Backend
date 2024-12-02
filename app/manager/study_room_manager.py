from fastapi import WebSocket

class StudyRoomManager:
    def __init__(self):
        self.study_room_connections={}
        self.online_user_connections={}
        self.connections={}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.connections[user_id] = websocket

    
    async def disconnect(self, user_id: str):
        if user_id in self.connections:
            del self.connections[user_id]


    async def send_message(self, user_id: str, message: dict):
        websocket = self.connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

