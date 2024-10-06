import random
import string
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List


app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_name: str):
        await websocket.accept()
        if chat_name not in self.active_connections:
            self.active_connections[chat_name] = []
        self.active_connections[chat_name].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_name: str):
        if chat_name in self.active_connections:
            self.active_connections[chat_name].remove(websocket)
            if not self.active_connections[chat_name]:
                del self.active_connections[chat_name]

    async def broadcast(self, message: str, chat_name: str):
        if chat_name in self.active_connections:
            for connection in self.active_connections[chat_name]:
                await connection.send_text(message)


manager = ConnectionManager()


# Генерация случайного имени пользователя
def generate_username() -> str:
    return ''.join(random.choices(string.ascii_letters, k=6))


@app.websocket('/chat/{chat_name}')
async def chat_endpoint(websocket: WebSocket, chat_name: str):
    username = generate_username()  # Присваиваем случайное имя пользователю
    await manager.connect(websocket, chat_name)
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message_to_send = f'{username} :: {data}'
            # Отправляем сообщение всем пользователям в комнате
            await manager.broadcast(message_to_send, chat_name)
    except WebSocketDisconnect:
        # Убираем пользователя из комнаты при отключении
        manager.disconnect(websocket, chat_name)
