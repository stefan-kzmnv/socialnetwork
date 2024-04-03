# I wrote this code

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User
from .serializers import UserProfileSerializer

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_profile_details(request, identifier):
    # Try to get the user by ID first.
    try:
        user_id = int(identifier)
        user = get_object_or_404(User, id=user_id)
    except ValueError:
        # If not an ID, try to get the user by username.
        user = get_object_or_404(User, username=identifier)

    user_profile = user.profile
    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_user_profile(request, identifier):
    # Try to get the user by ID first.
    try:
        user_id = int(identifier)
        user = get_object_or_404(User, id=user_id)
    except ValueError:
        # If not an ID, try to get the user by username.
        user = get_object_or_404(User, username=identifier)

    # Ensure the requesting user is the same as the user being updated.
    if request.user != user:
        return Response({"detail": "Not authorized to update this profile."}, status=status.HTTP_403_FORBIDDEN)

    user_profile = user.profile

    serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# end of code I wrote