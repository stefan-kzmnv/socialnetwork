# I wrote this code

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import *

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        # Exclude the current user from the friends queryset.
        if self.instance:
            self.fields['friends'].queryset = UserProfile.objects.exclude(id=self.instance.id)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

class FriendRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at')
    list_display = ('id', 'sender', 'recipient', 'created_at', 'accepted_at', 'status')

class StatusPostAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at')
    list_display = ('id', 'user', 'content', 'created_at')

class LikeAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at')
    list_display = ('user', 'post', 'created_at')

class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at')
    list_display = ('user', 'post', 'content', 'created_at')

class ImagePostAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'uploaded_at')
    list_display = ('id', 'user', 'image', 'uploaded_at')

class ChatRoomAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at')
    list_display = ('id', 'user1', 'user2', 'created_at')

class ChatMessageAdmin(admin.ModelAdmin):
    readonly_fields = ('room', 'sender', 'content', 'timestamp')
    list_display = ('room', 'sender', 'content', 'timestamp')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(StatusPost, StatusPostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ImagePost, ImagePostAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)

# end of code I wrote