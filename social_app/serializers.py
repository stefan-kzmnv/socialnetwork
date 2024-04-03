# I wrote this code

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db.models import Q

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login', 'is_active', 'date_joined']

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'recipient', 'created_at', 'accepted_at', 'status']

class StatusPostSerializer(serializers.ModelSerializer):
    num_likes = serializers.SerializerMethodField()

    class Meta:
        model = StatusPost
        fields = ['id', 'content', 'created_at', 'num_likes']

    def get_num_likes(self, obj):
        return obj.post_likes.count()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    post = StatusPostSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'post']

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagePost
        fields = ['id', 'image', 'uploaded_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['room', 'sender', 'content', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    chat_messages = ChatMessageSerializer(many=True, read_only=True, source='chat_messages.all')

    class Meta:
        model = ChatRoom
        fields = ['user1', 'user2', 'created_at', 'chat_messages']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    friends = serializers.StringRelatedField(many=True)
    sent_requests = FriendRequestSerializer(many=True, read_only=True)
    received_requests = FriendRequestSerializer(many=True, read_only=True)
    status_posts = StatusPostSerializer(source='user.status_posts', many=True, read_only=True)
    image_posts = ImagePostSerializer(source='user.imagepost_set', many=True, read_only=True)
    liked_posts = serializers.SerializerMethodField()
    comments = CommentSerializer(source='user.comments', many=True, read_only=True)
    chat_rooms = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_liked_posts(self, obj):
        liked_posts = StatusPost.objects.filter(post_likes__user=obj.user)
        return StatusPostSerializer(liked_posts, many=True).data
    
    def get_chat_rooms(self, obj):
        # Fetching chat rooms where the user is either user1 or user2.
        chat_rooms = ChatRoom.objects.filter(Q(user1=obj.user) | Q(user2=obj.user))
        return ChatRoomSerializer(chat_rooms, many=True).data

# end of code I wrote