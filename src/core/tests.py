from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CSRFTests(APITestCase):
    def test_csrf_returns_token_and_sets_cookie(self):
        response = self.client.get(reverse('core:csrf_token'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrf_token', response.data)
        self.assertIn('csrftoken', response.cookies)


class SetLanguageTests(APITestCase):
    def test_set_language_sets_cookie(self):
        response = self.client.post(
            reverse('core:set_language'), {'code': 'en'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'en',
        )

    def test_set_language_rejects_invalid_code(self):
        response = self.client.post(
            reverse('core:set_language'), {'code': 'de'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
