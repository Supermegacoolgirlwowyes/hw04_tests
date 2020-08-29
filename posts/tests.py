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

    # Тест на наличие профиля лежит в приложении users

    def check_post_on_page(self, url):
        with self.subTest(url=url):
            response = self.client.get(url)
            paginator = response.context.get('paginator')
            if paginator:
                self.assertEqual(paginator.count, 1)
                self.assertEqual(response.context['page'][0].author, self.post.author)
                self.assertEqual(response.context['page'][0].group, self.post.group)
                self.assertEqual(response.context['page'][0].text, self.post.text)
            else:
                self.assertEqual(response.context['post'].author, self.post.author)
                self.assertEqual(response.context['post'].group, self.post.group)
                self.assertEqual(response.context['post'].text, self.post.text)

    def test_Auth_New_Post(self):
        response = self.client_auth.post(
            reverse('new_post'), {
                'group': self.group.id,
                'text': 'created text'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = Post.objects.get(text='created text', group=self.group.id, author=self.user)
        self.assertTrue(response)

    def test_Not_Auth_New_Post(self):
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
        response = Post.objects.all()
        self.assertFalse(response)

    def test_Post_Published(self):
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='text'
        )
        url_list = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user}),
            reverse('post', kwargs={'username': self.user, 'post_id': self.post.id})
        ]
        for url in url_list:
            self.check_post_on_page(url)

    def test_Auth_User_Post_Edit(self):
        self.post = Post.objects.create(
            id=1,
            author=self.user,
            text='text'
        )
        self.group = Group.objects.create(
            title='dogs',
            slug='dogs'
        )
        post_edit_url = reverse('post_edit', kwargs={'username': self.post.author, 'post_id': self.post.id})
        self.client_auth.post(post_edit_url, {'text': 'updated text', 'group': self.group.id})
        self.post = Post.objects.get(text='updated text')

        url_list = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.post.author}),
            reverse('post', kwargs={'username': self.post.author, 'post_id': self.post.id}),
            reverse('group', kwargs={'slug': self.group.slug})
        ]

        for url in url_list:
            self.check_post_on_page(url)

    def test_404_page(self):
        group_url = reverse('group', kwargs={'slug': 'cars'})
        response = self.client.get(group_url)
        self.assertTrue(response.status_code == 404)

    def test_Post_Img_Tag(self):
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
            reverse('profile', kwargs={'username': self.user}),
            reverse('post', kwargs={'username': self.user, 'post_id': post.id}),
            reverse('group', kwargs={'slug': self.group.slug}),
        ]

        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '<img')

    def test_Post_Not_Image(self):
        not_img = SimpleUploadedFile(
            name='some.txt',
            content=b'abc',
            content_type='text/plain',
        )
        url = reverse('new_post')
        response = self.client_auth.post(
            url, {'text': 'Hahaha! I am uploding text, not image', 'image': not_img},
        )
        self.assertFormError(
            response, 'form', 'image', errors=(
                'Загрузите правильное изображение. '
                'Файл, который вы загрузили, поврежден '
                'или не является изображением.')
        )
