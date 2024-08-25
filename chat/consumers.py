from channels.generic.websocket import AsyncWebsocketConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer

class ChatConsumer(GenericAsyncAPIConsumer):
    async def connect(self):
        return await self.accept()
