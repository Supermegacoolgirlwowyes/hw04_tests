from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200, unique=True, blank=False, null=False
    )
    slug = models.SlugField(
        max_length=15, unique=True, blank=False, null=False
    )
    description = models.TextField(null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст',
        help_text='Напишите ваш пост здесь',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        blank=True,
        null=True,
        related_name='posts',
        help_text='Выберите группу (необязательно)',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите фотографию (необязательно)',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        author = self.author
        pub_date = self.pub_date
        text = self.text[:12]
        return f'{author}, {pub_date}, {text}...'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        'Текст',
        help_text='Напишите ваш комментарий',
    )
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        author = self.author
        pub_date = self.pub_date
        text = self.text[:12]
        return f'{author}, {pub_date}, {text}...'
