from django.test import TestCase, Client

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

    def testAuthUserNewPost(self):
        self.client.force_login(self.user)
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def testNotAuthUserNewPost(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=%2Fnew%2F', status_code=302, target_status_code=200)

    def testPublishPost(self):
        response_index = self.client.get('/')
        self.assertContains(response_index, self.post.text)
        response_profile = self.client.get('/username/')
        self.assertContains(response_profile, self.post.text)
        response_post = self.client.get('/username/1/')
        self.assertContains(response_post, self.post.text)
        response_post = self.client.get('/group/cats/')
        self.assertContains(response_post, self.post.text)

    def testAuthUserEditPost(self):
        self.client.force_login(self.user)
        response_read = self.client.get('/username/1/edit/')
        self.assertEqual(response_read.status_code, 200)

    def testEditedPost(self):
        Post.objects.filter(id=1).update(text='updated_text', group=self.group_dogs)
        response_index = self.client.get('/')
        self.assertContains(response_index, 'updated_text')
        response_profile = self.client.get('/username/')
        self.assertContains(response_profile, 'updated_text')
        response_post = self.client.get('/username/1/')
        self.assertContains(response_post, 'updated_text')
        response_post = self.client.get('/group/dogs/')
        self.assertContains(response_post, 'updated_text')
