import json
import logging

from fastapi import WebSocket
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, activity_id: int):
        if activity_id not in self.active_connections:
            self.active_connections[activity_id] = []
        self.active_connections[activity_id].append(websocket)

    def disconnect(self, websocket: WebSocket, activity_id: int):
        if activity_id in self.active_connections:
            if websocket in self.active_connections[activity_id]:
                self.active_connections[activity_id].remove(websocket)

    async def send_personal(self, event: BaseModel, websocket: WebSocket):
        await websocket.send_text(event.model_dump_json())

    async def send_personal_raw(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, event: BaseModel, activity_id: int):
        if activity_id in self.active_connections:
            text = event.model_dump_json()
            for connection in self.active_connections[activity_id]:
                try:
                    await connection.send_text(text)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")

    async def broadcast_raw(self, message: str, activity_id: int):
        if activity_id in self.active_connections:
            for connection in self.active_connections[activity_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")

    def get_connection_count(self, activity_id: int) -> int:
        return len(self.active_connections.get(activity_id, []))

    def has_connections(self, activity_id: int) -> bool:
        return bool(self.active_connections.get(activity_id))


manager = ConnectionManager()
