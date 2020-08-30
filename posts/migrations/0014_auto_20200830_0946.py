# Generated by Django 2.2.9 on 2020-08-30 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('pub_date',)},
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Напишите ваш пост здесь', max_length=20, verbose_name='Текст'),
        ),
    ]