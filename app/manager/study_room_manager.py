from datetime import datetime

from fastapi import WebSocket

from app.models import user

class StudyRoomManager:
    def __init__(self):
        self.study_room_connections={}
        self.online_user_connections={}
        self.connections={}

    # async def connect(self,connection:WebSocket,user_id:str,study_room_id:str):

    #     await connection.accept()
    #     if study_room_id not in self.connections:
    #         self.connections[study_room_id] = {}
    #     self.connections[study_room_id][user_id]=connection

    # async def disconnect(self, user_id: str, study_room_id: str):

    #     if study_room_id in self.connections and user_id in self.connections[study_room_id]:
    #         del self.connections[study_room_id][user_id]

    #         if not self.connections[study_room_id]:
    #             del self.connections[study_room_id]

    # async def send_message_to_room(self, study_room_id: str,user_id:str, message: str):
    #     if study_room_id in self.connections:
    #         for participants_id,connection in self.connections[study_room_id].items(): 
    #             try:
    #                 if user_id!=participants_id:
    #                     await connection.send_text(message)
    #             except Exception as e:
    #                 print(f"Error sending message to {user_id}: {e}")

            
    # async def broadcast(self, message: dict):
    #     for websocket in self.active_connections.values():
    #         await websocket.send_json(message)

    async def connect(self,connection:WebSocket,user_id:str):

    
        await connection.accept()
        self.connections[user_id]=connection

        timestamp = datetime.now().isoformat()
        message = {
            "type": "user-online",
            "data": {
                "user_id": user_id,
                "status": "online",
                "timestamp": timestamp
            }
        }
        await self.broadcast(message,user_id)

               
    async def disconnect(self,user_id:str):

        timestamp = datetime.now().isoformat()  
        message = {
            "type": "user-offline",
            "data": {
                "user_id": user_id,
                "status": "offline",
                "timestamp": timestamp
            }
        }
        await self.broadcast(message,user_id)
        del self.connections[user_id]


    async def broadcast(self, message: dict,user_id:str):
        for other_user_id, websocket in self.connections.items():
            if other_user_id != user_id: 
                await websocket.send_json(message)


    async def send_message(self, user_id: str, message: dict):
        websocket = self.connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

