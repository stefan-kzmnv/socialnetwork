# I wrote this code

import factory
from django.utils import timezone
from django.contrib.auth.models import User
from .models import *

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password')

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    birthday = factory.Faker('date_of_birth')
    workplace = factory.Faker('company')
    country = factory.Faker('country')
    city = factory.Faker('city')
    gender = factory.Iterator(UserProfile.GENDER_CHOICES, getter=lambda c: c[0])
    relationship_status = factory.Iterator(UserProfile.RELATIONSHIP_STATUS_CHOICES, getter=lambda c: c[0])
    avatar = factory.django.ImageField(filename='test_images/test_avatar.jpg')

class FriendRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FriendRequest

    sender = factory.SubFactory(UserProfileFactory)
    recipient = factory.SubFactory(UserProfileFactory)
    created_at = factory.LazyFunction(timezone.now)
    accepted_at = factory.LazyFunction(timezone.now)
    status = factory.Iterator(FriendRequest.STATUS_CHOICES, getter=lambda c: c[0])

class StatusPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StatusPost

    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)

class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(StatusPostFactory)
    created_at = factory.LazyFunction(timezone.now)

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)
    post = factory.SubFactory(StatusPostFactory)

class ImagePostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImagePost

    user = factory.SubFactory(UserFactory)
    image = factory.django.ImageField(filename='test_images/test_image.jpg')
    uploaded_at = factory.LazyFunction(timezone.now)

class ChatRoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRoom

    user1 = factory.SubFactory(UserFactory)
    user2 = factory.SubFactory(UserFactory)

class ChatMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMessage

    room = factory.SubFactory(ChatRoomFactory)
    sender = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')
    timestamp = factory.LazyFunction(timezone.now)

# end of code I wrote