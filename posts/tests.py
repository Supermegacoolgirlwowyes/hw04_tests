from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.user = User.objects.create_user(username='username')
        self.group = Group.objects.create(title='cats', slug='cats')
        self.client_auth.force_login(self.user)

    def check_post_on_page(self, url):
        with self.subTest(url=url):
            response = self.client.get(url)
            paginator = response.context.get('paginator')
            if paginator:
                response_post = response.context['page'][0]
                self.assertEqual(paginator.count, 1)
                self.assertEqual(response_post.author, self.post.author)
                self.assertEqual(response_post.group, self.post.group)
                self.assertEqual(response_post.text, self.post.text)
            else:
                response_post = response.context['post']
                self.assertEqual(response_post.author, self.post.author)
                self.assertEqual(response_post.group, self.post.group)
                self.assertEqual(response_post.text, self.post.text)

    def test_signup(self):
        self.client.post(
            reverse('signup'), {
                'username': 'supermegacoolgirlwowyes',
                'password1': 'N3wP4ssw0rd',
                'password2': 'N3wP4ssw0rd'
            }
        )
        user = User.objects.get(username='supermegacoolgirlwowyes')
        response = self.client.get(reverse('profile', args=[user.username]))
        self.assertEqual(response.status_code, 200)
        response = User.objects.all().count()
        self.assertEqual(response, 2)

    def test_auth_new_post(self):
        response = self.client_auth.post(
            reverse('new_post'), {
                'group': self.group.id,
                'text': 'created text'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = Post.objects.filter(
            text='created text',
            group=self.group.id,
            author=self.user
        ).count()
        self.assertEqual(response, 1)
        response = Post.objects.all().count()
        self.assertEqual(response, 1)

    def test_not_auth_new_post(self):
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        target_url = f'{login_url}?next={new_post_url}'
        response = self.client.get(f'{new_post_url}')
        self.assertRedirects(response, target_url, target_status_code=200)
        self.client.post(
            reverse('new_post'), {
                'group': self.group.id,
                'text': 'created text'
            },
            follow=True
        )
        response = Post.objects.all().count()
        self.assertFalse(response, 0)

    def test_post_published(self):
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='text'
        )
        url_list = [
            reverse('index'),
            reverse('profile', args=[self.user]),
            reverse('post', args=[self.user, self.post.id])
        ]
        for url in url_list:
            self.check_post_on_page(url)

    def test_auth_user_post_edit(self):
        self.post = Post.objects.create(
            id=1,
            author=self.user,
            text='text'
        )
        self.group = Group.objects.create(
            title='dogs',
            slug='dogs'
        )
        post_edit_url = reverse(
            'post_edit',
            args=[
                self.post.author,
                self.post.id
            ]
        )
        self.client_auth.post(
            post_edit_url, {
                'text': 'updated text',
                'group': self.group.id
            }
        )
        self.post = Post.objects.get(text='updated text')

        url_list = [
            reverse('index'),
            reverse('profile', args=[self.post.author]),
            reverse(
                'post',
                args=[
                    self.post.author,
                    self.post.id
                ]
            ),
            reverse('group', args=[self.group.slug])
        ]

        for url in url_list:
            self.check_post_on_page(url)

    def test_404_page(self):
        group_url = reverse('group', kwargs={'slug': 'cars'})
        response = self.client.get(group_url)
        self.assertTrue(response.status_code == 404)

    def test_post_img_tag(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        img = SimpleUploadedFile(
            name='img.gif',
            content=small_gif,
            content_type='image/jpeg',
        )
        self.client_auth.post(
            reverse('new_post'), {
                'author': self.user,
                'text': 'My cat image',
                'image': img,
                'group': self.group.id
            },
        )
        post = Post.objects.get(id=1)

        url_list = [
            reverse('index'),
            reverse('profile', args=[self.user]),
            reverse('post', args=[self.user, post.id]),
            reverse('group', args=[self.group.slug]),
        ]

        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '<img')

    def test_post_not_image(self):
        not_img = SimpleUploadedFile(
            name='some.txt',
            content=b'abc',
            content_type='text/plain',
        )
        url = reverse('new_post')
        response = self.client_auth.post(
            url, {
                'text': 'Hahaha! I am uploding text, not image',
                'image': not_img
            },
        )
        self.assertFormError(
            response, 'form', 'image', errors=(
                'Загрузите правильное изображение. '
                'Файл, который вы загрузили, поврежден '
                'или не является изображением.')
        )
