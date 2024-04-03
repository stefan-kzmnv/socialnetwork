# I wrote this code

import tempfile
from PIL import Image
from io import BytesIO
from django.test import TestCase, Client
from django.test import override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from ..models import *

@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SocialAppViewsTests(TestCase):

    def setUp(self):
        # Create test users.
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.status = StatusPost.objects.create(user=self.user1, content="Test status")
        self.client = Client()
    
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

    def test_profile_view(self):
        # Login as user1.
        self.client.login(username='user1', password='password123')
        
        response = self.client.get(reverse('profile', args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_app/profile.html')

    def test_custom_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'user1', 'password': 'password123'})
        self.assertRedirects(response, reverse('profile', args=[self.user1.username]))

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'user3',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_edit_profile_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'John',
            'last_name': 'Doe',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_app/edit_profile.html')

    def test_send_friend_request(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('send_friend_request', args=[self.user2.id]))
        self.assertTrue(FriendRequest.objects.filter(sender=self.user1.profile, recipient=self.user2.profile).exists())
        self.assertRedirects(response, reverse('profile', args=[self.user1.username]))

    def test_accept_friend_request(self):
        # Create a friend request from user1 to user2.
        friend_request = FriendRequest.objects.create(sender=self.user1.profile, recipient=self.user2.profile)
        
        self.client.login(username='user2', password='password123')
        response = self.client.post(reverse('accept_friend_request', args=[friend_request.id]))
        self.assertTrue(self.user1.profile in self.user2.profile.friends.all())
        self.assertRedirects(response, reverse('profile', args=[self.user2.username]))

    def test_decline_friend_request(self):
        # Create a friend request from user1 to user2.
        friend_request = FriendRequest.objects.create(sender=self.user1.profile, recipient=self.user2.profile)
        
        self.client.login(username='user2', password='password123')
        response = self.client.post(reverse('decline_friend_request', args=[friend_request.id]))
        self.assertFalse(FriendRequest.objects.filter(id=friend_request.id).exists())
        self.assertRedirects(response, reverse('profile', args=[self.user2.username]))

    def test_unfriend(self):
        # Make user1 and user2 friends.
        self.user1.profile.friends.add(self.user2.profile)
        
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('unfriend', args=[self.user2.profile.id]))
        self.assertFalse(self.user2.profile in self.user1.profile.friends.all())
        self.assertRedirects(response, reverse('profile', args=[self.user1.username]))

    def test_all_friends_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('all_friends', args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_app/all_friends.html')

    def test_search_results_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('search_results'), {'search_query': 'user2'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_app/search_results.html')

    def test_all_posts_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('all_posts', args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social_app/all_posts.html')

    def test_post_status_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('post_status'), {
            'content': 'This is a new status!'
        })
        self.assertRedirects(response, reverse('profile', args=[self.user1.username]))

    def test_like_status_view(self):
        self.client.login(username='user1', password='password123')
        # Provide a referrer URL in the headers.
        response = self.client.get(reverse('like_status', args=[self.status.id]), HTTP_REFERER=reverse('profile', args=[self.user1.username]))
        # Check if the status was liked.
        self.assertTrue(Like.objects.filter(user=self.user1, post=self.status).exists())
        # Check if the user was redirected to the referrer URL.
        self.assertEqual(response.status_code, 302)

    def test_add_comment_view(self):
        self.client.login(username='user1', password='password123')
        # Provide a referrer URL in the headers.
        response = self.client.post(reverse('add_comment', args=[self.status.id]), {
            'content': 'This is a test comment'
        }, HTTP_REFERER=reverse('profile', args=[self.user1.username]))
        # Check if the comment was added.
        self.assertTrue(Comment.objects.filter(user=self.user1, post=self.status, content='This is a test comment').exists())
        # Check if the user was redirected to the referrer URL.
        self.assertEqual(response.status_code, 302)
    
    def test_chat_room_view(self):
        self.client.login(username='user1', password='password123')
        room = ChatRoom.objects.create(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('chat_room', args=[room.id]))
        self.assertEqual(response.status_code, 200)

    def test_start_chat_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('start_chat', args=[self.user2.id]))
        # Expecting a redirect to the chat room.
        self.assertEqual(response.status_code, 302)

    def test_all_messages_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('all_messages'))
        self.assertEqual(response.status_code, 200)

    def generate_test_image(self):
        # Generate an image using PIL.
        image = Image.new('RGB', (100, 100), color = 'red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return SimpleUploadedFile(name='test_image.jpg', content=image_io.getvalue(), content_type='image/jpeg')

    def test_upload_image_view(self):
        # Use the function above to generate a test image.
        image = self.generate_test_image()
        response = self.client.post(reverse('upload_image'), {'image': image})
        # Expecting a redirect after upload.
        self.assertEqual(response.status_code, 302)

    def test_all_images_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('all_images', args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'images')

# end of code I wrote