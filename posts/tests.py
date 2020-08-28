from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Post, Group


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.user = User.objects.create(username='username')
        self.group = Group.objects.create(title='cats', slug='cats')
        self.client_auth.force_login(self.user)

    def test_AuthNewPost(self):
        response = self.client_auth.post(reverse('new_post'), {'group': self.group.id, 'text': 'text'})
        self.assertTrue(response)

    def test_NotAuthNewPost(self):
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        target_url = f'{login_url}?next={new_post_url}'
        response = self.client.get(f'{new_post_url}')
        self.assertRedirects(response, target_url, target_status_code=200)

    def test_Post_Published(self):
        self.client_auth.post(reverse('new_post'), {'group': self.group.id, 'text': 'text'})
        post = Post.objects.get(pk=1)

        index_url = reverse('index')
        profile_url = reverse('profile', kwargs={'username': self.user})
        post_url = reverse('post', kwargs={'username': self.user, 'post_id': post.id})

        url_list = [index_url, profile_url]

        for url in url_list:
            response = self.client.get(url)
            self.assertIn(post, response.context['page'])

        response = self.client.get(post_url)
        self.assertEqual(post, response.context['post'])

    def test_Auth_User_Post_Edit(self):
        post = Post.objects.create(
            id=1,
            author=self.user,
            text='text'
        )
        post_edit_url = reverse('post_edit', kwargs={'username': post.author, 'post_id': post.id})
        self.client_auth.post(post_edit_url, {'text': 'new text', 'group': self.group.id})

        index_url = reverse('index')
        profile_url = reverse('profile', kwargs={'username': post.author})
        post_url = reverse('post', kwargs={'username': post.author, 'post_id': post.id})
        group_url = reverse('group', kwargs={'slug': self.group.slug})

        url_list = [index_url, profile_url, post_url, group_url]

        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, 'new text')

    def test_404page(self):
        group_url = reverse('group', kwargs={'slug': 'cars'})
        response = self.client.get(group_url)
        self.assertTrue(response.status_code == 404)
