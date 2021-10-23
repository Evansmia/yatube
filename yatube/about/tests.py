from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages(self):
        list_of_pages = [
            '/about/author/',
            '/about/tech/',
        ]
        for page in list_of_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)
