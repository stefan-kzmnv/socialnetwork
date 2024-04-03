# I wrote this code

import os
import collections
import tempfile
from django.test import TestCase
from django.conf import settings
from django.test import override_settings
from rest_framework.utils.serializer_helpers import ReturnList

from ..model_factories import *
from ..serializers import *

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class UserSerializerTest(TestCase):
    user = None
    user_serializer = None

    def setUp(self):
        self.user = UserFactory.create()
        self.user_serializer = UserSerializer(self.user)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        # Delete the user's avatar image if there was one
        if self.user.profile.avatar:
            avatar_path = os.path.join(settings.MEDIA_ROOT, self.user.profile.avatar.name)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

    def test_userSerializerInitialization(self):
        self.assertIsNotNone(self.user)
    
    def test_userSerializerHasExpectedFields(self):
        data = self.user_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'username',
                                                'first_name', 'last_name',
                                                'email', 'last_login',
                                                'is_active', 'date_joined']))
    
    def test_userSerializerFieldsAreInExpectedFormat(self):
        data = self.user_serializer.data
        self.assertIs(type(data['id']), int)
        self.assertIs(type(data['username']), str)
        self.assertIs(type(data['first_name']), str)
        self.assertIs(type(data['last_name']), str)
        self.assertIs(type(data['email']), str)
        self.assertIs(type(data['last_login']), type(None))
        self.assertIs(type(data['is_active']), bool)
        self.assertIs(type(data['date_joined']), str)

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class UserProfileSerializerTest(TestCase):
    user_1 = None
    user_2 = None
    user_profile_serializer = None
    status_posts = None
    chat_rooms = None

    def setUp(self):
        # This will also create an associated UserProfile due to the signal
        self.user_1 = UserFactory.create()
        self.user_2 = UserFactory.create()
        # Build a UserProfile instance without saving it to get the data
        profile_data = UserProfileFactory.build()

        # Update the fields of the automatically created UserProfile
        self.user_1.profile.birthday = profile_data.birthday
        self.user_1.profile.workplace = profile_data.workplace
        self.user_1.profile.country = profile_data.country
        self.user_1.profile.city = profile_data.city
        self.user_1.profile.gender = profile_data.gender
        self.user_1.profile.relationship_status = profile_data.relationship_status
        self.user_1.profile.avatar = profile_data.avatar
        # Save the updated UserProfile instance
        self.user_1.profile.save()

        self.status_posts = StatusPostFactory.create(user=self.user_1)
        self.chat_rooms = ChatRoomFactory.create(user1=self.user_1, user2=self.user_2)
        self.profile_serializer = UserProfileSerializer(self.user_1.profile)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        # Delete the user's avatar image if there was one
        if self.user_1.profile.avatar:
            avatar_path = os.path.join(settings.MEDIA_ROOT, self.user_1.profile.avatar.name)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

    def test_userProfileSerializerInitialization(self):
        self.assertIsNotNone(self.user_1.profile)
    
    def test_userProfileSerializerHasExpectedFields(self):
        data = self.profile_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'user',
                                                'avatar', 'birthday',
                                                'country', 'city',
                                                'workplace', 'gender',
                                                'relationship_status', 'image_posts',
                                                'liked_posts', 'status_posts',
                                                'sent_requests', 'received_requests',
                                                'comments', 'friends',
                                                'chat_rooms']))

    def test_userProfileSerializerFieldsAreInitializedInExpectedFormat(self):
        data = self.profile_serializer.data
        self.assertIs(type(data['id']), int)
        self.assertEqual(data['user'].keys(), set(['id', 'username',
                                                'first_name', 'last_name',
                                                'email', 'last_login',
                                                'is_active', 'date_joined']))
        self.assertIs(type(data['avatar']), str)
        self.assertIs(type(data['birthday']), str)
        self.assertIs(type(data['country']), str)
        self.assertIs(type(data['city']), str)
        self.assertIs(type(data['workplace']), str)
        self.assertIs(type(data['gender']), str)
        self.assertIs(len(data['gender']), 1)
        self.assertIs(type(data['relationship_status']), str)
        self.assertIs(len(data['relationship_status']), 1)
        self.assertIs(type(data['image_posts']), list)
        self.assertIs(type(data['liked_posts']), ReturnList)
        self.assertIs(type(data['status_posts']), list)
        self.assertIs(type(data['sent_requests']), list)
        self.assertIs(type(data['received_requests']), list)
        self.assertIs(type(data['comments']), list)
        self.assertIs(type(data['friends']), list)
        self.assertIs(type(data['chat_rooms']), ReturnList)

class FriendRequestTest(TestCase):
    user_1 = None
    user_2 = None
    friend_request = None
    friend_request_serializer = None

    def setUp(self):
        self.user_1 = UserFactory.create()
        self.user_2 = UserFactory.create()
        self.friend_request = FriendRequestFactory.create(sender=self.user_1.profile, recipient=self.user_2.profile)
        self.friend_request_serializer =  FriendRequestSerializer(self.friend_request)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_friendRequestSerializerInitialization(self):
        self.assertIsNotNone(self.friend_request)
    
    def test_friendRequestSerializerHasExpectedFields(self):
        data = self.friend_request_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'sender',
                                                'recipient', 'created_at',
                                                'accepted_at', 'status']))
    
    def test_friendRequestFieldsAreInExpectedFormat(self):
        data = self.friend_request_serializer.data
        self.assertIs(type(data['id']), int)
        # Foreign key
        self.assertIs(type(data['sender']), int)
        # Foreign key
        self.assertIs(type(data['recipient']), int)
        self.assertIs(type(data['created_at']), str)
        self.assertIs(type(data['accepted_at']), str)
        self.assertIs(type(data['status']), str)

class StatusPostTest(TestCase):
    user = None
    status_post = None
    status_post_serializer = None

    def setUp(self):
        self.user = UserFactory.create()
        self.status_post = StatusPostFactory.create(user=self.user)
        self.status_post_serializer =  StatusPostSerializer(self.status_post)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_statusPostSerializerInitialization(self):
        self.assertIsNotNone(self.status_post)
    
    def test_statusPostSerializerHasExpectedFields(self):
        data = self.status_post_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'num_likes',
                                                'content', 'created_at']))
    
    def test_statusPostFieldsAreInExpectedFormat(self):
        data = self.status_post_serializer.data
        self.assertIs(type(data['id']), int)
        self.assertIs(type(data['content']), str)
        self.assertIs(type(data['num_likes']), int)
        self.assertIs(type(data['created_at']), str)

class LikeTest(TestCase):
    user = None
    status_post = None
    like = None
    like_serializer = None

    def setUp(self):
        self.user = UserFactory.create()
        self.status_post = StatusPostFactory.create(user=self.user)
        self.like = LikeFactory.create(user=self.user, post=self.status_post)
        self.like_serializer =  LikeSerializer(self.like)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_likeSerializerInitialization(self):
        self.assertIsNotNone(self.like)
    
    def test_likeSerializerHasExpectedFields(self):
        data = self.like_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'user',
                                                'post', 'created_at']))
    
    def test_likeFieldsAreInExpectedFormat(self):
        data = self.like_serializer.data
        self.assertIs(type(data['id']), int)
        # Foreign key
        self.assertIs(type(data['user']), int)
        # Foreign key
        self.assertIs(type(data['post']), int)
        self.assertIs(type(data['created_at']), str)

class CommentTest(TestCase):
    user = None
    status_post = None
    comment = None
    comment_serializer = None

    def setUp(self):
        self.user = UserFactory.create()
        self.status_post = StatusPostFactory.create(user=self.user)
        self.comment = CommentFactory.create(user=self.user, post=self.status_post)
        self.comment_serializer = CommentSerializer(self.comment)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_commentSerializerInitialization(self):
        self.assertIsNotNone(self.comment)
    
    def test_commentSerializerHasExpectedFields(self):
        data = self.comment_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'content',
                                                'post', 'created_at']))
    
    def test_commentFieldsAreInExpectedFormat(self):
        data = self.comment_serializer.data
        self.assertIs(type(data['id']), int)
        self.assertIs(type(data['content']), str)
        # Foreign key
        self.assertIs(type(data['post']), collections.OrderedDict)
        self.assertIs(type(data['created_at']), str)

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImagePostTest(TestCase):
    user = None
    image_post = None
    image_post_serializer = None

    def setUp(self):
        self.user = UserFactory.create()
        self.image_post = ImagePostFactory.create(user=self.user)
        self.image_post_serializer = ImagePostSerializer(self.image_post)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        # Delete the image post's image
        if self.image_post.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image_post.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)

    def test_imagePostSerializerInitialization(self):
        self.assertIsNotNone(self.image_post)
    
    def test_imagePostSerializerHasExpectedFields(self):
        data = self.image_post_serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'image', 'uploaded_at']))
    
    def test_imagePostFieldsAreInExpectedFormat(self):
        data = self.image_post_serializer.data
        self.assertIs(type(data['id']), int)
        self.assertIs(type(data['image']), str)
        self.assertIs(type(data['uploaded_at']), str)

class ChatRoomSerializerTest(TestCase):
    user_1 = None
    user_2 = None
    chat_room = None
    chat_room_serializer = None

    def setUp(self):
        self.user_1 = UserFactory.create()
        self.user_2 = UserFactory.create()
        self.chat_room = ChatRoomFactory.create(user1=self.user_1, user2=self.user_2)
        self.chat_room_serializer = ChatRoomSerializer(self.chat_room)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_chatRoomSerializerInitialization(self):
        self.assertIsNotNone(self.chat_room)
    
    def test_chatRoomSerializerHasExpectedFields(self):
        data = self.chat_room_serializer.data
        self.assertEqual(set(data.keys()), set(['user1', 'user2',
                                                'created_at', 'chat_messages']))
    
    def test_chatRoomFieldsAreInExpectedFormat(self):
        data = self.chat_room_serializer.data
        # Foreign key
        self.assertIs(type(data['user1']), int)
        # Foreign key
        self.assertIs(type(data['user2']), int)
        self.assertIs(type(data['created_at']), str)
        self.assertIs(type(data['chat_messages']), list)

class ChatMessageSerializerTest(TestCase):
    user_1 = None
    user_2 = None
    chat_room = None
    chat_message = None
    chat_message_serializer = None

    def setUp(self):
        self.user_1 = UserFactory.create()
        self.user_2 = UserFactory.create()
        self.chat_room = ChatRoomFactory.create(user1=self.user_1, user2=self.user_2)
        self.chat_message = ChatMessageFactory.create(room=self.chat_room, sender=self.user_1)
        self.chat_room_serializer = ChatMessageSerializer(self.chat_message)
    
    def tearDown(self):
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        ImagePost.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
        StatusPost.objects.all().delete()
        FriendRequest.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_chatMessageSerializerInitialization(self):
        self.assertIsNotNone(self.chat_message)
    
    def test_chatMessageSerializerHasExpectedFields(self):
        data = self.chat_room_serializer.data
        self.assertEqual(set(data.keys()), set(['room', 'sender',
                                                'content', 'timestamp']))
    
    def test_chatMessageFieldsAreInExpectedFormat(self):
        data = self.chat_room_serializer.data
        # Foreign key
        self.assertIs(type(data['room']), int)
        # Foreign key
        self.assertIs(type(data['sender']), int)
        self.assertIs(type(data['content']), str)
        self.assertIs(type(data['timestamp']), str)

# end of code I wrote