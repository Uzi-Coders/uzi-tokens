from django.conf import settings
from django.utils import translation


class CookieOnlyLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = self._get_language(request)

        translation.activate(language)
        request.LANGUAGE_CODE = language

        try:
            response = self.get_response(request)
            response.setdefault("Content-Language", language)
            return response
        finally:
            translation.deactivate()

    @staticmethod
    def _get_language(request):
        language = request.COOKIES.get(
            settings.LANGUAGE_COOKIE_NAME,
            ""
        )

        if not isinstance(language, str):
            return settings.LANGUAGE_CODE

        language = language.strip().lower()

        supported = {
            code.lower()
            for code, _ in settings.LANGUAGES
        }

        if language in supported:
            return language

        return settings.LANGUAGE_CODE
