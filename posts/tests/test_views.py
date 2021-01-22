from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Follow, Post, Group


User = get_user_model()

POSTS_PER_PAGE = 12

class ViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='VladOs')
        cls.another_user_author = User.objects.create(username='Elon95')
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.group = Group.objects.create(            
            title='Группа для теста',
            slug='test-group',
            description='Группа для теста')
        cls.group_01 = Group.objects.create(            
            title='Группа для теста 01',
            slug='test-group01',
            description='Группа01 для теста')
        cls.post = Post.objects.create(
            text = 'Текст теста',
            author = cls.user_author,
            group = cls.group,)
        cls.post_01 = Post.objects.create(
            text = 'Текст теста01',
            author = cls.user_author,
            group = cls.group_01,
            image = uploaded)
        cls.post_02 = Post.objects.create(
            text = 'Текст теста01',
            author = cls.another_user_author,
            group = cls.group_01,
            image = uploaded)
    
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(ViewTest.user_author)
        self.another_post_author = Client()
        self.another_post_author.force_login(ViewTest.another_user_author)
    
    def test_pages_uses_correct_template(self):
        """URL-адреса использует соответствующие шаблоны."""
        templates_pages_name={
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs=
            {'slug': ViewTest.group.slug}),
            'new.html': reverse('new_post'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')}
        for template, reverse_name in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('index'))
        expected = ViewTest.post_02
        post_context = response.context.get('page')[0]
        self.assertEqual(post_context, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('group', kwargs=
            {'slug': ViewTest.group.slug}))
        expected = Group.objects.get(slug=ViewTest.group.slug)
        group_context = response.context.get('group')
        self.assertEqual(group_context, expected)
    
    def test_post_creation_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        models_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
        for value, expected in models_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def test_new_post_with_group_shown_in_expected_group(self):
        """Сформированный пост отображается корректно
        на странице выбранной группы."""
        response = self.authorized_client.get(reverse('group', kwargs=
            {'slug': ViewTest.group_01.slug}))
        group_title = response.context.get('group')
        post_title = response.context.get('page')[1].image
        expected_group = ViewTest.post_01.group
        expected_image = ViewTest.post_01.image
        self.assertEqual(group_title, expected_group)
        self.assertEqual(post_title, expected_image)

    def test_new_post_with_group_shown_in_main_page(self):
        """Сформированный пост с указанной группой
        отображается корректно на главной странице."""
        response = self.authorized_client.get(reverse('index'))
        index = response.context.get('page')[0].text
        expected = ViewTest.post_01.text
        self.assertEqual(index, expected)
   
    def test_edit_posts_show_correct_context(self):
        """Содержимое словаря context для страницы 
        редактирования поста."""
        username = ViewTest.user_author.username
        post_id = ViewTest.post.id
        response = self.post_author.get(
            reverse('post_edit', kwargs={
            'username': username,
            'post_id': post_id})
            )
        models_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        expected_author = ViewTest.post.author
        page_context_author = response.context.get('post').author
        for value, expected in models_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(page_context_author, expected_author)
    
    def test_user_profile_show_correct_context(self):
        """Содержимое словаря context для страницы 
        профиля пользователя."""
        username = self.user_author.username
        username2 = self.another_user_author.username
        response = self.authorized_client.get(
            reverse('profile', kwargs={
            'username': username})
            )
        response2 = self.authorized_client.get(
            reverse('profile', kwargs={
            'username': username2})
            )
        expected_post = ViewTest.post
        expected_author = ViewTest.post.author
        expected_image = ViewTest.post_02.image
        page_context = response.context.get('page')[0]
        page_context_author = response.context.get('post').author
        page_context_image = response2.context.get('page')[0].image
        self.assertEqual(page_context, expected_post)
        self.assertEqual(page_context_author, expected_author)
        self.assertEqual(page_context_image, expected_image)

    def test_one_post_show_correct_context(self):
        """Содержимое словаря context для страницы 
        отдельного поста."""
        username = self.user_author.username
        username2 = self.another_user_author.username
        post_id = ViewTest.post.id
        post_id2 = ViewTest.post_02.id
        response = self.authorized_client.get(
            reverse('post', kwargs={
            'username': username,
            'post_id': post_id})
            )
        response2 = self.authorized_client.get(
            reverse('post', kwargs={
            'username': username2,
            'post_id': post_id2})
            )
        expected = ViewTest.post
        expected_image = ViewTest.post_02.image
        post_context = response.context.get('post')
        post_context_image = response2.context.get('post').image
        self.assertEqual(post_context, expected)
        self.assertEqual(post_context_image, expected_image)
    
    def test_paginator(self):
        """Проверка паджинатора на гл. странице."""
        objs = (Post(author=ViewTest.user_author, text='Test %s' % i) for i in range(20))
        Post.objects.bulk_create(objs)
        response = self.guest_client.get(reverse('index'))
        response_2_page = self.guest_client.get(reverse('index') + '?page=2')
        all_posts_length = len(response.context.get('paginator').object_list)
        self.assertEqual(len(response.context.get('page').object_list), POSTS_PER_PAGE)
        self.assertEqual(len(response_2_page.context.get('page').object_list), all_posts_length - POSTS_PER_PAGE)

    def test_cache(self):
        """Тест кэша """
        html_0 = self.guest_client.get('/')
        html_1 = self.guest_client.get('/')
        self.assertHTMLEqual(
            str(html_0.content), 
            str(html_1.content),
            'Что-то пошло не так'
            )
    
    def test_follow_and_unfollow(self):
        """Тест подписок и отписок."""
        Follow.objects.create(user=self.user, author=ViewTest.user_author)
        self.assertTrue(Follow.objects.filter(author=ViewTest.user_author).exists())
        Follow.objects.filter(user=self.user, author=ViewTest.user_author).delete()
        self.assertFalse(Follow.objects.filter(author=ViewTest.user_author).exists())
    
    def test_new_post_with_follows_author_is_correct(self):
        """Сформированный пост на подписанного автора
        отображается в ленте подписчиков."""
        Follow.objects.create(user=self.user, author=ViewTest.user_author)
        response = self.authorized_client.get(reverse('follow_index'))
        index = response.context.get('page')[0].text
        expected = ViewTest.post.text
        self.assertEqual(index, expected)
