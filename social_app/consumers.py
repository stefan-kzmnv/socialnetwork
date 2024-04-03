# I wrote this code

import json
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        chat_room = await self.get_room_instance()

        # Set the room_group_name attribute.
        self.room_group_name = f'chat_{self.room_id}'

        # Check if the user is one of the friends associated with the chat room.
        user1, user2 = await self.get_chat_room_users(chat_room)

        if not chat_room or self.scope["user"].id not in [user1.id, user2.id]:
            # Reject the connection.
            await self.close()
            return

        # Accept the WebSocket connection.
        await self.accept()

        # Load the last 20 chat_messages from the database.
        chat_messages = await self.get_last_20_chat_messages()

        for chat_message in reversed(chat_messages):
            message_data = await self.get_message_data(chat_message)
            await self.send(text_data=json.dumps({
                'chat_message': message_data['content'],
                'username': message_data['username'],
                'timestamp': message_data['timestamp']
            }))

        # Join room group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def get_last_20_chat_messages(self):
        return list(ChatMessage.objects.filter(room__id=self.room_id).order_by('-timestamp')[:20])

    @sync_to_async
    def get_room_instance(self):
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None
    
    @sync_to_async
    def get_message_data(self, chat_message):
        return {
            "username": chat_message.sender.username,
            "content": chat_message.content,
            "timestamp": chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @sync_to_async
    def get_chat_room_users(self, chat_room):
        return chat_room.user1, chat_room.user2

    async def disconnect(self, close_code):
        # Leave room group.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive chat_message from WebSocket.
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        chat_message = text_data_json['chat_message']

        # Try to retrieve the ChatRoom instance.
        room_instance = await self.get_room_instance()
        if not room_instance:
            await self.send(text_data=json.dumps({
                'error': 'No such room exists.'
            }))
            return

        # Save the chat_message to the database.
        await self.save_chat_message(room_instance, chat_message)

        # Send chat_message, username, and timestamp to room group.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'chat_message': chat_message,
                'username': self.scope["user"].username,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
    
    @sync_to_async
    def get_room_instance(self):
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @sync_to_async
    def save_chat_message(self, room_instance, chat_message):
        ChatMessage.objects.create(
            sender=self.scope["user"],
            room=room_instance,
            content=chat_message
        )

    # Receive chat_message from room group.
    async def chat_message(self, event):
        chat_message = event['chat_message']
        username = event['username']
        timestamp = event['timestamp']

        # Send raw message, username, and timestamp to WebSocket.
        await self.send(text_data=json.dumps({
            'chat_message': chat_message,
            'username': username,
            'timestamp': timestamp
        }))

# end of code I wrote