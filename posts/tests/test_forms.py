from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='VladOs')
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='test-group',
            description='Группа для теста'
        )
        cls.post = Post.objects.create(
            text='Текст теста',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user_author)
        self.post_author = Client()
        self.post_author.force_login(PostFormTest.user_author)

    def test_new_post_creation(self):
        """Проверка создания нового поста."""
        post_count = Post.objects.count()
        small_gif = (
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
            )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text='Тестовый текст').exists())

    def test_post_edit(self):
        """Проверка редактирования поста."""
        username = self.user_author.username
        post_id = PostFormTest.post.id
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый текст'
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': username,
                'post_id': post_id}
            ),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Post.objects.filter(
            text='Тестовый текст'),
            form_data['text']
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_comment(self):
        """Только авторизированный пользователь может комментировать посты."""
        username = self.user_author.username
        post_id = PostFormTest.post.id
        comments_count = Comment.objects.count()
        form_data = {'text': 'Текст тестового комментария'}
        self.authorized_client.post(
            reverse('add_comment', kwargs={
                'username': username,
                'post_id': post_id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_comment_not_authrorized(self):
        """Не авториз. пользователь не может комментировать посты."""
        username = self.user_author.username
        post_id = PostFormTest.post.id
        comments_count = Comment.objects.count()
        form_data = {'text': 'Текст тестового комментария'}
        self.guest_client.post(
            reverse('add_comment', kwargs={
                'username': username,
                'post_id': post_id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertNotEqual(Comment.objects.count(), comments_count + 2)
