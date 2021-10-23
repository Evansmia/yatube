import shutil
import tempfile


from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.core.cache import cache


from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Описание',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='HasNoName')

        for post in range(11):
            Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=PostsPagesTests.group
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            image=self.uploaded,
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )
        self.group_2 = Group.objects.create(
            title='Тестовый заголовок_2',
            description='Описание_2',
            slug='test-slug_2'
        )

    def test_pages_uses_correct_template(self):
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list',
             kwargs={'slug': 'test-slug'})): 'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse('posts:profile',
             kwargs={'username': 'HasNoName'})): 'posts/profile.html',
            (reverse('posts:post_detail',
             kwargs={'post_id': self.post.id})): 'posts/post_detail.html',
            (reverse('posts:post_edit',
             kwargs={'post_id': self.post.id})): 'posts/create_post.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'test-slug'}))
        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'HasNoName'})
                                              )
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_post_detail_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})))
        test = response.context['post'].id
        self.assertEqual(test, self.post.id)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        reverse_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        ]
        for page_name in reverse_pages_names:
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(page_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_two_records(self):
        reverse_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        ]
        for page_name in reverse_pages_names:
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(page_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 2)

    def test_post_in_group(self):
        reverse_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        ]
        for page_name in reverse_pages_names:
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(page_name)
                self.assertIn(self.post,
                              response.context['page_obj'])

    def test_post_not_in_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug_2'}))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object.group.title
        group_description_0 = first_object.group.description
        group_slug_0 = first_object.group.slug
        self.assertEqual(group_title_0, 'Тестовый заголовок')
        self.assertEqual(group_description_0, 'Описание')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertTrue(first_object.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            (reverse('posts:profile', kwargs={'username': 'HasNoName'})))
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object.group.title
        group_description_0 = first_object.group.description
        group_slug_0 = first_object.group.slug
        self.assertEqual(group_title_0, 'Тестовый заголовок')
        self.assertEqual(group_description_0, 'Описание')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertTrue(first_object.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            (reverse('posts:group_list', kwargs={'slug': 'test_slug'})))
        first_object = response.context['page_obj'][0]
        group_title_0 = first_object.group.title
        group_description_0 = first_object.group.description
        group_slug_0 = first_object.group.slug
        self.assertEqual(group_title_0, 'Тестовый заголовок')
        self.assertEqual(group_description_0, 'Описание')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertTrue(first_object.image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id})))
        count = response.context['count']
        test_count = Post.objects.filter(author=self.post.user).count()
        self.assertEqual(count, test_count)
        test_post = self.post
        text_obj = response.context['post']
        image_obj = text_obj.image
        self.assertEqual(test_post, text_obj)
        self.assertTrue(image_obj, self.post.image)

    def test_cache(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            response,
            self.authorized_client.get(reverse('posts:index')).content
        )
        cache.clear()
        self.assertNotEqual(
            response,
            self.authorized_client.get(reverse('posts:index')).content
        )
