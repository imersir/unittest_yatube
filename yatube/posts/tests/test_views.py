from django import forms
from django.conf import settings as st
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='leo1')
        cls.author_authorized = Client()
        cls.author_authorized.force_login(cls.author)

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.author,
            group=cls.group,
            id='1',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='leo2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # какой шаблон будет вызван при обращении
    # к view-классам через соответствующий 'name'
    def test_url_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),  # главной страницы
            'group.html': reverse('group_posts',
                                  kwargs={'slug': self.group.slug}),
            # страницы группы
            'new.html': reverse('new_post'),  # страницы создания поста
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # соответствует ли ожиданиям словарь context, передаваемый в шаблон
    # главной страницы
    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['posts'][0]
        text = first_object.text
        group = first_object.group
        self.assertEqual(text, PostPagesTests.post.text)
        self.assertEqual(group, PostPagesTests.group)

    # страницы группы
    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'].title,
                         PostPagesTests.group.title)
        self.assertEqual(response.context['group'].slug,
                         PostPagesTests.group.slug)

    # 1. страницы создания поста
    # 2. страницы редактирования поста /<username>/<post_id>/edit/
    def test_new_post_edit_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.author_authorized.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    # страницы профайла пользователя /<username>/,
    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.post.author}))
        first_object = response.context['page'][0]
        self.assertEqual(first_object.text, PostPagesTests.post.text)
        self.assertEqual(first_object.group, PostPagesTests.post.group)

    # страницы отдельного поста /<username>/<post_id>/
    def test_post_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': self.post.author,
                                    'post_id': self.post.id}))
        first_object = response.context['post']
        self.assertEqual(first_object.text, PostPagesTests.post.text)
        self.assertEqual(first_object.author, PostPagesTests.post.author)


# Проверка,что если при создании поста указать группу, то этот пост появляется
class GroupPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo1')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='slug',
        )
        cls.group2 = Group.objects.create(
            title='Заголовок2',
            slug='slug2',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
        )
        cls.post2 = Post.objects.create(
            text='Текст2',
            author=cls.user,
            group=cls.group2,
        )

    # на странице выбранной группы
    def test_group_list_pages_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'slug'}))
        group_object = response.context['posts'][0]
        self.assertEqual(group_object.text, self.post.text)
        self.assertNotEqual(group_object.text, self.post2.text)


# Проверка пагинатора
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='leo')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(title='Группа', slug='slug')

        Post.objects.bulk_create([Post(
            text=f'Тестовое сообщение{i}',
            author=cls.user, group=cls.group)
            for i in range(13)])

    def test_paginator_full_pages(self):
        urls_name = [
            reverse('index'),  # на главной странице
            reverse('group_posts', kwargs={'slug': self.group.slug}),
            # страница группы
            reverse('profile', kwargs={'username': self.user})
            # страница профайла
        ]
        for name in urls_name:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    st.PAGINATOR_NUMBER_OF_PAGES)
