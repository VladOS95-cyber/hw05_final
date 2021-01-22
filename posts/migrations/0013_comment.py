# Generated by Django 2.2.6 on 2021-01-21 08:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0012_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Напишите комментарий', verbose_name='Текст коммента')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Дата добавляется автоматически', verbose_name='Дата комментария')),
                ('author', models.ForeignKey(help_text='Имя автора добавляется автоматически', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Имя автора')),
                ('post', models.ForeignKey(blank=True, help_text='Комментируемый пост', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='posts.Post', verbose_name='Пост')),
            ],
        ),
    ]
