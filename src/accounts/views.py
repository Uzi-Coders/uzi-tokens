from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.db import transaction as db_transaction
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAuthenticated

from . import serializers

User = get_user_model()


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with db_transaction.atomic():
            if User.objects.count() >= settings.MAX_USERS:
                return Response(
                    {'message': _("User cannot be created.")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = serializer.save()

        login(request, user)

        return Response(
            {
                'message': _("Account created successfully."),
                'user': serializers.UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        return Response(
            {
                'message': _("Logged in successfully."),
                'user': serializers.UserSerializer(user).data,
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {'message': _("Logged out successfully.")},
            status=status.HTTP_200_OK
        )
