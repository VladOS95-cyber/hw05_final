from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='VladOs')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            description='Тестовое описание группы',
            slug='test-group'
        )
        Post.objects.create(
            text='т' * 50,
            author=cls.user_author,
            group=cls.group
        )
        cls.post = Post.objects.get(id=1)

    def test_object_text_len_field(self):
        post = ModelsTest.post
        expected_test = post.text[:15]
        self.assertEquals(expected_test, str(post))

    def test_object_title_is_str_field(self):
        group = ModelsTest.group
        expected_object_title = group.title
        self.assertEqual(expected_object_title, str(group))

    def test_verbose(self):
        """verbose_name поля совпадает с ожидаемым."""
        post = ModelsTest.post
        verbose_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Имя автора',
            'group': 'Группа'
        }
        for value, expected in verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text поля совпадает с ожидаемым."""
        post = ModelsTest.post
        help_texts = {
            'text': 'Введите текст поста для публикации.',
            'pub_date': 'Дата добавляется автоматически',
            'group': 'Выберите группу'
        }
        for value, expected in help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
