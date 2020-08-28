from django.test import TestCase, Client
from django.urls import reverse

from django.contrib.auth import get_user_model


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        self.client.post(
            reverse('signup'), {
                'username': 'supermegacoolgirlwowyes', 'password1': 'N3wP4ssw0rd', 'password2': 'N3wP4ssw0rd'
            }
        )
        user = get_user_model().objects.get(id=1)
        response = self.client.get(reverse('profile', kwargs={'username': user.username}))
        self.assertEqual(response.status_code, 200)
