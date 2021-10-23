from django.contrib.auth import get_user_model
from django.test import TestCase, Client


from posts.models import Group, Post


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Описание',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_urls_exists_at_desired_location(self):
        list_of_pages = ['/', '/group/test-slug/',
                         '/profile/HasNoName/', f'/posts/{self.post.id}/', ]
        for item in list_of_pages:
            with self.subTest(item=item):
                response = self.guest_client.get(item)
                self.assertEqual(response.status_code, 200)

    def test_unexisting_page_url_exists_at_desired_location(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_post_edit_and_create_url_exists_at_desired_location(self):
        list_of_pages = [
            '/create/',
            f'/posts/{self.post.id}/edit/',
        ]
        for page in list_of_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_create_and_post_edit_pages_url_redirect_anonymous(self):
        list_of_pages = [
            '/create/',
            f'/posts/{self.post.id}/edit/',
        ]
        for page in list_of_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in url_templates_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
