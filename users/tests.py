from django.test import TestCase, Client

from posts.models import User


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='username')

    def test_signup(self):
        response = self.client.get('/username/')
        self.assertEqual(response.status_code, 200)
