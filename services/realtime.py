from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id].remove(websocket)

    async def broadcast(self, message: dict, user_id: str):
        for connection in self.active_connections.get(user_id, []):
            await connection.send_json(message)
