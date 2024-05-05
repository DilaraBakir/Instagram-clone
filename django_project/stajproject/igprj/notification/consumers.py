import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f'notifications_{self.scope["user"].id}'
        await self.add_groups()
        await self.accept()

    @database_sync_to_async
    def add_groups(self):
        for user_id in User.objects.values_list("id", flat=True):
            self.channel_layer.group_add(f'notifications_{user_id}', self.channel_name)

    def disconnect(self, close_code):
        for user in User.objects.all():
            async_to_sync(self.channel_layer.group_discard)(f'notifications_{user.id}', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'like':
            post_id = data.get('post_id')
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')

            await self.channel_layer.group_send(
                f"notifications_{receiver_id}",
                {
                    'type': 'send_notification',
                    'notification': {
                        'action': action,
                        'sender_id': sender_id,
                        'post_id': post_id,
                    }
                }
            )

    async def send_notification(self, event):
        message = event['notification']
        await self.send(text_data=json.dumps({'message': message}))

