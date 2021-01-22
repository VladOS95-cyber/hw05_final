from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='test-group',
            description='Группа для теста'
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.user_author,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Какой то коммент',
            author=cls.user_author
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='VladOs')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(URLTests.user_author)

    def test_new_post_creation(self):
        """Доступ к страницам автора поста."""
        urls_pages_names = {
            '/': 200,
            '/group/test-group/': 200,
            '/new/': 200,
            '/about/author/': 200,
            '/about/tech/': 200,
            f'/{URLTests.user_author.username}/': 200,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/': 200,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/edit/': 200,
            '/Несуществующее имя/': 404
        }
        for url, code in urls_pages_names.items():
            response = self.post_author.get(url)
            self.assertEqual(response.status_code, code)

    def test_urls_access_guest_client(self):
        """Доступ к страницам неавториз. пользователям."""
        urls_pages_names = {
            '/': 200,
            '/group/test-group/': 200,
            '/new/': 302,
            '/about/author/': 200,
            '/about/tech/': 200,
            f'/{URLTests.user_author.username}/': 200,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/': 200,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/edit/': 302,
            '/Несуществующее имя/': 404,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/comment': 302
        }
        for url, code in urls_pages_names.items():
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, code)

    def test_urls_access_authorized_client(self):
        """Доступ к страницам авториз. пользователям
        не автор поста."""
        urls_pages_names = {
            '/': 200,
            '/group/test-group/': 200,
            '/new/': 200,
            '/about/author/': 200,
            '/about/tech/': 200,
            f'/{URLTests.user_author.username}/': 200,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/': 200,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/edit/': 302,
            '/Несуществующее имя/': 404,
            f'/{URLTests.user_author.username}/{URLTests.post.id}/comment': 200
        }
        for url, code in urls_pages_names.items():
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """Тест вызова HTML шаблонов."""
        templates_url_names={
            'index.html': '/',
            'group.html': '/group/test-group/',
            'new.html': '/new/',
            'new.html':
                f'/{URLTests.user_author.username}/{URLTests.post.id}/edit/',
            'post.html':
                f'/{URLTests.user_author.username}/{URLTests.post.id}/',
            'profile.html': f'/{URLTests.user_author.username}/',
            'misc/404.html': 'Несуществующее имя/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.post_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_task_detail_url_redirect_anonymous(self):
        """Страница по адресу /<username>/<post_id>/edit/ перенаправит анонимного
        пользователя на страницу авторизации.
        А авториз. пользователя, не автора постана главную страницу."""
        response_guest = self.guest_client.get(
            f'/{URLTests.user_author.username}/{URLTests.post.id}/edit/',
            follow=True
        )
        respone_authorized = self.authorized_client.get(
            f'/{URLTests.user_author.username}/{URLTests.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response_guest,
            f'/auth/login/?next=/{URLTests.user_author.username}/{URLTests.post.id}/edit/'
        )
        self.assertRedirects(respone_authorized, reverse('index'))
