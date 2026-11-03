from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.utils.translation import activate, gettext as _
from django.conf import settings


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFTokenAPIView(APIView):
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return Response({'csrf_token': csrf_token}, status=status.HTTP_200_OK)

    permission_classes = [AllowAny]


class SetLanguageAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code')
        if not isinstance(code, str):
            return Response({'error': _("Invalid language code.")}, status=status.HTTP_400_BAD_REQUEST)

        code = code.strip().lower()
        if code not in ('fa', 'en'):
            return Response({'error': _("Invalid language code.")}, status=status.HTTP_400_BAD_REQUEST)

        activate(code)
        response = Response({'message': _("Language changed to %s") % code})
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response
