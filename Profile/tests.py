from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Request, Comment


class RequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.request = Request.objects.create(
            user=self.user,
            title="Test Request",
            body="This is a test request."
        )

    def test_request_creation(self):
        self.assertEqual(self.request.title, "Test Request")
        self.assertEqual(self.request.status, 'pending')
        self.assertIsNotNone(self.request.slug)

class HomePageViewTest(TestCase):
    def test_home_page_template_used(self):
        response = self.client.get(reverse('home_page'))
        self.assertTemplateUsed(response, 'start-page/home.html')

from .forms import RequestForm

class RequestFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'title': 'Test Title',
            'body': 'Test Body'
        }
        form = RequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'title': '', 'body': 'Test Body'}
        form = RequestForm(data=form_data)
        self.assertFalse(form.is_valid())

class URLTest(TestCase):
    def test_home_url(self):
        response = self.client.get(reverse('home_page'))
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
