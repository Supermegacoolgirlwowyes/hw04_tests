from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        self.client.post(
            reverse('signup'), {
                'username': 'supermegacoolgirlwowyes',
                'password1': 'N3wP4ssw0rd',
                'password2': 'N3wP4ssw0rd'
            }
        )
        response = User.objects.filter(username='supermegacoolgirlwowyes').count()
        self.assertEqual(response, 1)
