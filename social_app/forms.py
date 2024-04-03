# I wrote this code

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length = 30,
        required = True,
        label = "First Name",
        widget = forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    last_name = forms.CharField(
        max_length = 30,
        required = True,
        label = "Last Name",
        widget = forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    password = forms.CharField(
        label = "Password",
        required = False,
        widget = forms.PasswordInput(attrs={'class': 'form-control shadow-none'})
    )

    avatar = forms.ImageField(
        label = "Avatar",
        required = False,
        widget = forms.FileInput(attrs={'class': 'form-control shadow-none'})
    )
    workplace = forms.CharField(
        max_length = 255,
        label = "Workplace",
        required = False,
        widget = forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    city = forms.CharField(
        max_length = 100,
        label = "City",
        required = False,
        widget = forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    country = forms.CharField(
        max_length = 100,
        label = "Country",
        required = False,
        widget = forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    birthday = forms.DateField(
        label = "Birthday",
        required = False,
        widget = forms.DateInput(
            attrs = {
                'class': 'form-control shadow-none',
                'placeholder': 'YYYY-MM-DD'
            }
        )
    )
    gender = forms.ChoiceField(
        choices = UserProfile.GENDER_CHOICES,
        label = "Gender",
        widget = forms.Select(attrs={'class': 'form-control shadow-none'})
    )
    relationship_status = forms.ChoiceField(
        choices = UserProfile.RELATIONSHIP_STATUS_CHOICES,
        label = "Relationship status",
        widget = forms.Select(attrs={'class': 'form-control shadow-none'})
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'birthday', 'workplace', 'country', 'city', 'gender', 'relationship_status']

    def save(self, user, commit=True):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        user.save()

        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label = 'Username',
        widget = forms.TextInput(attrs={'class': 'form-control shadow-none'}),
        label_suffix = '',
    )
    password = forms.CharField(
        label = 'Password',
        widget = forms.PasswordInput(attrs={'class': 'form-control shadow-none'}),
        label_suffix = '',
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label = 'Email',
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    username = forms.CharField(
        required=True,
        label = 'Username',
        widget=forms.TextInput(attrs={'class': 'form-control shadow-none'})
    )
    password1 = forms.CharField(
        required=True,
        label = 'Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control shadow-none'})
    )
    password2 = forms.CharField(
        required=True,
        label = 'Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control shadow-none'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class StatusPostForm(forms.ModelForm):
    class Meta:
        model = StatusPost
        fields = ['content']

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImagePost
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

# end of code I wrote