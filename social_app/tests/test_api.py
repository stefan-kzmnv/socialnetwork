# I wrote this code

import os
import tempfile
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from ..model_factories import *
from ..serializers import UserProfileSerializer

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class UserProfileDetailsTests(APITestCase):
    user = None
    profile_data = None
    token = None

    def setUp(self):
        self.user = UserFactory.create()
        # Build a UserProfile instance without saving it to get the data
        profile_data = UserProfileFactory.build()

        # Update the fields of the automatically created UserProfile
        self.user.profile.birthday = profile_data.birthday
        self.user.profile.workplace = profile_data.workplace
        self.user.profile.country = profile_data.country
        self.user.profile.city = profile_data.city
        self.user.profile.gender = profile_data.gender
        self.user.profile.relationship_status = profile_data.relationship_status
        self.user.profile.avatar = profile_data.avatar
        # Save the updated UserProfile instance
        self.user.profile.save()
        
        # Create a token for the user
        self.token = Token.objects.create(user=self.user)
    
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

    def test_unauthenticatedRequest(self):
        response = self.client.get(reverse('user-profile-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_authenticatedRequestWithInvalidToken(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalid_token')
        response = self.client.get(reverse('user-profile-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_authenticatedRequestWithValidToken(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.get(reverse('user-profile-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)  # OK

    def test_getUserById(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.get(reverse('user-profile-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['id'], self.user.id)

    def test_getUserByUsername(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.get(reverse('user-profile-detail', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], self.user.username)

    def test_invalidIdentifier(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.get(reverse('user-profile-detail', args=['invalid_identifier']))
        self.assertEqual(response.status_code, 404)  # Not Found

    def test_responseStructure(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.get(reverse('user-profile-detail', args=[self.user.id]))
        self.assertIn('user', response.data)
        self.assertIn('friends', response.data)
        self.assertIn('sent_requests', response.data)
        self.assertIn('received_requests', response.data)
        self.assertIn('status_posts', response.data)
        self.assertIn('image_posts', response.data)
        self.assertIn('liked_posts', response.data)
        self.assertIn('comments', response.data)
        self.assertIn('chat_rooms', response.data)
        self.assertIn('birthday', response.data)
        self.assertIn('workplace', response.data)
        self.assertIn('country', response.data)
        self.assertIn('city', response.data)
        self.assertIn('gender', response.data)
        self.assertIn('relationship_status', response.data)
        self.assertIn('avatar', response.data)

    def test_dataIntegrity(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.get(reverse('user-profile-detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)  # OK
        # Deserialize the response data
        serialized_data = UserProfileSerializer(self.user.profile).data
        # Compare the response data against the serialized data
        self.assertEqual(response.data, serialized_data)

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class UpdateUserProfileTests(APITestCase):
    user = None
    profile_data = None
    token = None

    def setUp(self):
        self.user = UserFactory.create()
        # Build a UserProfile instance without saving it to get the data
        profile_data = UserProfileFactory.build()

        # Update the fields of the automatically created UserProfile
        self.user.profile.birthday = profile_data.birthday
        self.user.profile.workplace = profile_data.workplace
        self.user.profile.country = profile_data.country
        self.user.profile.city = profile_data.city
        self.user.profile.gender = profile_data.gender
        self.user.profile.relationship_status = profile_data.relationship_status
        self.user.profile.avatar = profile_data.avatar
        # Save the updated UserProfile instance
        self.user.profile.save()
        
        # Create a token for the user
        self.token = Token.objects.create(user=self.user)
    
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

    def test_unauthenticatedRequest(self):
        response = self.client.post(reverse('update-user-profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_authenticatedRequestWithInvalidToken(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalid_token')
        response = self.client.post(reverse('update-user-profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_updateOwnProfile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        data = {'city': 'New City'}
        response = self.client.post(reverse('update-user-profile', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 200)  # OK
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.city, 'New City')

    def test_updateAnotherUsersProfile(self):
        another_user = UserFactory()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        data = {'city': 'New City'}
        response = self.client.post(reverse('update-user-profile', args=[another_user.id]), data)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_invalidData(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        data = {'birthday': 'invalid_date'}
        response = self.client.post(reverse('update-user-profile', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 400)  # Bad Request

    def test_nonexistentUser(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token.key))
        response = self.client.post(reverse('update-user-profile', args=['non_existent_user']))
        self.assertEqual(response.status_code, 404)  # Not Found

# end of code I wrote