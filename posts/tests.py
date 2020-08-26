from django.test import TestCase, Client
from django.urls import reverse

from posts.models import User, Post, Group


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='username')
        self.group_cats = Group.objects.create(title='cats', slug='cats')
        self.group_dogs = Group.objects.create(title='dogs', slug='dogs')
        self.post = Post.objects.create(
            id=1,
            author=self.user,
            group=self.group_cats,
            text='text'
        )

    def testAuthNewPost(self):
        new_post_url = reverse('new_post')

        self.client.force_login(self.user)
        response = self.client.post(f'{new_post_url}', {'group': self.group_cats, 'text': self.post.text})
        self.assertEqual(response.status_code, 200)

    def testNotAuthNewPost(self):
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        target_url = f'{login_url}?next={new_post_url}'

        response = self.client.get(f'{new_post_url}')
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def testPostPublished(self):
        profile_url = reverse('profile', kwargs={'username': self.post.author})
        post_url = reverse('post', kwargs={'username': self.post.author, 'post_id': self.post.id})
        group_url = reverse('group', kwargs={'slug': self.post.group})

        response_index = self.client.get('/')
        self.assertContains(response_index, self.post.text)

        response_profile = self.client.get(f'{profile_url}')
        self.assertContains(response_profile, self.post.text)

        response_post = self.client.get(f'{post_url}')
        self.assertContains(response_post, self.post.text)

        response_post = self.client.get(f'{group_url}')
        self.assertContains(response_post, self.post.text)

    def testAuthUserEditPost(self):
        post_edit_url = reverse('post_edit', kwargs={'username': self.post.author, 'post_id': self.post.id})
        self.client.force_login(self.user)
        response = self.client.post(f'{post_edit_url}', {'id': 1, 'group': 'group_updated', 'text': 'text_updated'})
        self.assertEqual(response.status_code, 200)

    def testEditedPost(self):
        Post.objects.filter(id=1).update(text='updated_text', group=self.group_dogs)

        profile_url = reverse('profile', kwargs={'username': self.post.author})
        post_url = reverse('post', kwargs={'username': self.post.author, 'post_id': self.post.id})
        group_url = reverse('group', kwargs={'slug': self.group_dogs.slug})

        response_index = self.client.get('/')
        self.assertContains(response_index, self.post.text)

        response_profile = self.client.get(f'{profile_url}')
        self.assertContains(response_profile, self.post.text)

        response_post = self.client.get(f'{post_url}')
        self.assertContains(response_post, self.post.text)

        response_post = self.client.get(f'{group_url}')
        self.assertContains(response_post, self.post.text)

    def test404page(self):
        group_url = reverse('group', kwargs={'slug': 'cars'})
        response = self.client.get(f'{group_url}')
        self.assertTrue(response.status_code == 404)
