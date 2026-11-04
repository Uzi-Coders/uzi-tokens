from django.utils.translation import gettext as _
from django.conf import settings
from django.db import IntegrityError, transaction as db_transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import IsAuthenticated

from .models import User, ApiToken
from . import serializers


class ApiTokenListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = ApiToken.objects.filter(user=request.user).order_by("-created_at")
        return Response(
            serializers.ApiTokenSerializer(tokens, many=True).data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = serializers.ApiTokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        api_token = None
        with db_transaction.atomic():
            User.objects.select_for_update().get(pk=request.user.pk)

            if ApiToken.objects.filter(user=request.user).count() >= settings.MAX_API_TOKENS_PER_USER:
                return Response(
                    {'message': _(
                        "You cannot have more than %(limit)s API tokens."
                    ) % {'limit': settings.MAX_API_TOKENS_PER_USER}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for _attempt in range(5):
                try:
                    with db_transaction.atomic():
                        api_token = ApiToken.objects.create(
                            user=request.user,
                            name=serializer.validated_data['name'],
                            token=ApiToken.generate_key(),
                            permission=serializer.validated_data['permission'],
                        )
                    break
                except IntegrityError:
                    continue

        if api_token is None:
            return Response(
                {'message': _("Could not create the API token. Please try again.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            serializers.ApiTokenSerializer(api_token, context={'reveal_full_key': True}).data,
            status=status.HTTP_201_CREATED
        )


class ApiTokenDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, token_id):
        deleted, _rows = ApiToken.objects.filter(pk=token_id, user=request.user).delete()
        if not deleted:
            return Response(
                {'message': _("API token not found.")},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiTokenRevealView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token_id):
        try:
            api_token = ApiToken.objects.get(pk=token_id, user=request.user)
        except ApiToken.DoesNotExist:
            return Response(
                {'message': _("API token not found.")},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {'token': api_token.token},
            status=status.HTTP_200_OK
        )
