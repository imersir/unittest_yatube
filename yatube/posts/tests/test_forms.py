from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='leo2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='slug',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
        )

    # 1. проверки формы создания нового поста (страница /new/)
    # 2. если указать группу, то пост появляется на глав. странице
    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(reverse('new_post'),
                                               data=form_data, )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Текст', group=self.group.id).exists())

    # проверка, что при редактировании поста через форму на странице
    # /<username>/<post_id>/edit/ изменяется соответствующая запись.
    def test_post_edit_form(self):
        """Редактирование поста"""
        form_data = {
            'text': 'Меняю текст',
            'group': self.group.id
        }
        self.authorized_client.post(reverse('post_edit',
                                            kwargs={'username': 'leo2',
                                                    'post_id': self.post.id}),
                                    data=form_data)
        self.assertEqual(Post.objects.get(id=1).text, form_data['text'])
