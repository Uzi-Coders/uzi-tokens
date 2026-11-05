from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ApiToken

User = get_user_model()


class ApiTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', password='S3cure-pass-123',
        )
        self.other = User.objects.create_user(
            username='bob', password='S3cure-pass-123',
        )
        self.client.force_authenticate(self.user)

    def test_list_requires_authentication(self):
        self.client.force_authenticate(None)

        response = self.client.get(reverse('tokens:api_tokens'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_returns_full_token(self):
        response = self.client.post(
            reverse('tokens:api_tokens'),
            {'name': 'ci-token', 'permission': 'read_write'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['token'].startswith(settings.API_TOKEN_PREFIX))
        self.assertNotEqual(response.data['token'], response.data['masked_token'])
        self.assertIn('*', response.data['masked_token'])

        token = ApiToken.objects.get(user=self.user)
        self.assertEqual(token.permission, ApiToken.Permission.READ_WRITE)

    def test_create_token_defaults_to_read(self):
        response = self.client.post(
            reverse('tokens:api_tokens'), {'name': 'ci-token'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['permission'], ApiToken.Permission.READ)

    def test_list_only_returns_own_tokens(self):
        ApiToken.objects.create(
            user=self.user, name='mine', token=ApiToken.generate_key(),
        )
        ApiToken.objects.create(
            user=self.other, name='theirs', token=ApiToken.generate_key(),
        )

        response = self.client.get(reverse('tokens:api_tokens'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['name'] for item in response.data], ['mine'])

    def test_reveal_returns_full_token(self):
        api_token = ApiToken.objects.create(
            user=self.user, name='ci-token', token=ApiToken.generate_key(),
        )

        response = self.client.post(
            reverse('tokens:api_token_reveal', kwargs={'token_id': api_token.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], api_token.token)

    def test_reveal_other_users_token_returns_404(self):
        api_token = ApiToken.objects.create(
            user=self.other, name='ci-token', token=ApiToken.generate_key(),
        )

        response = self.client.post(
            reverse('tokens:api_token_reveal', kwargs={'token_id': api_token.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_removes_token(self):
        api_token = ApiToken.objects.create(
            user=self.user, name='ci-token', token=ApiToken.generate_key(),
        )

        response = self.client.delete(
            reverse('tokens:api_token_detail', kwargs={'token_id': api_token.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ApiToken.objects.filter(pk=api_token.pk).exists())

    @override_settings(MAX_API_TOKENS_PER_USER=1)
    def test_create_is_blocked_at_limit(self):
        ApiToken.objects.create(
            user=self.user, name='one', token=ApiToken.generate_key(),
        )

        response = self.client.post(
            reverse('tokens:api_tokens'), {'name': 'two'}, format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ApiToken.objects.filter(user=self.user).count(), 1)
