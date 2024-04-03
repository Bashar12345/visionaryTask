# views.py
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password

# from models import models
from .models import CustomUser


from .serializers import UserRegistrationSerializer, UserLoginSerializer

from rest_framework.permissions import AllowAny  # Import AllowAny permission class


# class UserRegistrationView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserRegistrationSerializer
#     permission_classes = [AllowAny]  # Allow unauthenticated access


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # Read existing data from JSON file
        with open("data.json", "r") as f:
            data = json.load(f)

        # Deserialize request data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Hash the password before saving to JSON file
        serializer.validated_data["password"] = make_password(
            serializer.validated_data["password"]
        )

        # Append new user data to existing users list
        users_data = data.get("users", [])
        users_data.append(serializer.validated_data)

        # Write updated data back to JSON file
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


from django.contrib.auth import get_user_model


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Load user data from the JSON file
        with open("data.json", "r") as f:
            users_data = json.load(f).get("users", [])

        # Find user with the given email
        user_data = next((u for u in users_data if u["email"] == email), None)

        if not user_data:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the provided password matches the hashed password in the JSON data
        if not check_password(password, user_data["password"]):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get the User model
        User = get_user_model()

        # Check if the user already exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # If the user does not exist, create a new one
            user = User.objects.create_user(
                username=email,  # Use email as username or provide a suitable username
                email=email,
                password=password,
            )

        # If the password matches, proceed with login
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
