# I wrote this code

from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import LogoutView
from .views import *
from .api import *

urlpatterns = [
    # Authentication.
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),

    # Profiles.
    path('accounts/edit_profile/', edit_profile, name='edit_profile'),
    path('accounts/<str:username>/', profile, name='profile'),

    # Search and friends.
    path('search_results/', search_results, name='search_results'),
    path('send_friend_request/<int:user_id>', send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>', accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>', decline_friend_request, name='decline_friend_request'),
    path('all_friends/<str:username>/', all_friends, name='all_friends'),
    path('unfriend/<int:friend_id>/', unfriend, name='unfriend'),

    # Posting status and image updates.
    path('all_posts/<str:username>/', all_posts, name='all_posts'),
    path('post_status/', post_status, name='post_status'),
    path('like_status/<int:status_id>/', like_status, name='like_status'),
    path('add_comment/<int:status_id>/', add_comment, name='add_comment'),
    path('upload_image/', upload_image, name='upload_image'),
    path('all_images/<str:username>/', all_images, name='all_images'),

    # Chatting.
    path('start_chat/<int:friend_id>/', start_chat, name='start_chat'),
    path('chat/<str:room_id>/', chat_room, name='chat_room'),
    path('all_messages/', all_messages, name='all_messages'),

    # API.
    path('api/user-profile/<str:identifier>/', user_profile_details, name='user-profile-detail'),
    path('api/update-profile/<str:identifier>/', update_user_profile, name='update-user-profile'),
]

urlpatterns += staticfiles_urlpatterns()

# end of code I wrote