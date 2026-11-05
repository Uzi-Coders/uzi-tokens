from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class SignupTests(APITestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('accounts:signup'),
            {'username': 'alice', 'password': 'S3cure-pass-123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'alice')
        self.assertIsNone(response.data['user']['first_name'])
        self.assertIsNone(response.data['user']['last_name'])
        self.assertIsNone(response.data['user']['email'])
        self.assertNotIn('id', response.data['user'])
        user = User.objects.get(username='alice')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_accepts_optional_profile_fields(self):
        response = self.client.post(
            reverse('accounts:signup'),
            {
                'username': 'alice',
                'password': 'S3cure-pass-123',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'email': 'alice@example.com',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['first_name'], 'Alice')
        self.assertEqual(response.data['user']['last_name'], 'Smith')
        self.assertEqual(response.data['user']['email'], 'alice@example.com')

    def test_signup_accepts_null_optional_profile_fields(self):
        response = self.client.post(
            reverse('accounts:signup'),
            {
                'username': 'alice',
                'password': 'S3cure-pass-123',
                'first_name': None,
                'last_name': None,
                'email': None,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['user']['first_name'])
        self.assertIsNone(response.data['user']['last_name'])
        self.assertIsNone(response.data['user']['email'])

    def test_signup_rejects_duplicate_username(self):
        User.objects.create_user(username='alice', password='S3cure-pass-123')

        response = self.client.post(
            reverse('accounts:signup'),
            {'username': 'alice', 'password': 'S3cure-pass-123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    @override_settings(MAX_USERS=1)
    def test_signup_is_blocked_when_max_users_is_reached(self):
        User.objects.create_user(username='alice', password='S3cure-pass-123')

        response = self.client.post(
            reverse('accounts:signup'),
            {'username': 'bob', 'password': 'S3cure-pass-123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='bob').exists())


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='S3cure-pass-123',
        )

    def test_login_starts_session(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'alice', 'password': 'S3cure-pass-123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'alice', 'password': 'wrong-password'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('_auth_user_id', self.client.session)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='S3cure-pass-123',
        )

    def test_logout_ends_session(self):
        self.client.login(username='alice', password='S3cure-pass-123')

        response = self.client.post(reverse('accounts:logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_requires_authentication(self):
        response = self.client.post(reverse('accounts:logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
