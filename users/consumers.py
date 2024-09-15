import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import User

class NotificationConsumer(AsyncWebsocketConsumer):
    connected_users = set()

    async def connect(self):
        user_id = self.scope['user'].id
        group_name = f'user_{user_id}'
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        self.connected_users.add(user_id)
        print(self.connected_users)
        await self.accept()

    async def disconnect(self, close_code):
        user_id = self.scope['user'].id
        group_name = f'user_{user_id}'
        await self.channel_layer.group_discard(
            group_name,
            self.channel_name
        )
        self.connected_users.discard(user_id)
        
        
    async def notify(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
