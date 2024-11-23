from fastapi import WebSocket

from app.models import user


class StudyRoomManager:
    def __init__(self):
        self.connections={}

    async def connect(self,connection:WebSocket,user_id:str,study_room_id:str):

        await connection.accept()
        if study_room_id not in self.connections:
            self.connections[study_room_id] = {}
        self.connections[study_room_id][user_id]=connection

    
    async def disconnect(self, user_id: str, study_room_id: str):

        if study_room_id in self.connections and user_id in self.connections[study_room_id]:
            del self.connections[study_room_id][user_id]

            # if study rooms become empty
            if not self.connections[study_room_id]:
                del self.connections[study_room_id]


    async def send_message_to_room(self, study_room_id: str,user_id:str, message: str):
        
        if study_room_id in self.connections:
            for participants_id,connection in self.connections[study_room_id].items():  
                try:
                    if user_id!=participants_id:
                        print("hellp")
                        await connection.send_text(message)
                except Exception as e:
                    print(f"Error sending message to {user_id}: {e}")