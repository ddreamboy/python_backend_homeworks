import pytest
from websockets import connect

# URL WebSocket сервера
WS_URL = 'ws://localhost:8000/chat/testroom'

@pytest.mark.asyncio
async def test_websocket_chat():
    async with connect(WS_URL) as websocket1, connect(WS_URL) as websocket2:
        # Получение приветственных сообщений
        welcome_message1 = await websocket1.recv()
        welcome_message2 = await websocket2.recv()

        assert 'Добро пожаловать в чат!' in welcome_message1
        assert 'Добро пожаловать в чат!' in welcome_message2

        # Извлечение имен пользователей из приветственных сообщений
        username1 = welcome_message1.split('::')[-1].strip()
        username2 = welcome_message2.split('::')[-1].strip()

        # Отправка сообщения от первого клиента
        await websocket1.send('Привет от клиента 1')
        received_message = await websocket2.recv()

        assert f'{username1} :: Привет от клиента 1' in received_message

        # Отправка сообщения от второго клиента
        await websocket2.send('Привет от клиента 2')
        received_message = await websocket1.recv()

        assert f'{username2} :: Привет от клиента 2' in received_message