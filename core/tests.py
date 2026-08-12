from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email='admin@test.com', name='Test Admin', role='ADMIN', password='Passw0rd!'
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_email(self):
        ok = self.client.login(email='admin@test.com', password='Passw0rd!')
        self.assertTrue(ok)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_logged_in_user_reaches_dashboard(self):
        self.client.login(email='admin@test.com', password='Passw0rd!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
