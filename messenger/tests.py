import unittest
# from django.test import TestCase
# from .models import CustomUser
# from django.urls import reverse
# # Create your tests here.
# API_URL='/api/messenger'


from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import *
API_URL='/api/'

# class ViewTestCase(TestCase):
#     """Test suite for the api views."""

#     def setUp(self):
#         """Define the test client and other test variables."""
#         self.client = APIClient()
#         self.user_data = {
#             'email': 'test@gmail.com',""
class ViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse(API_URL+'users_register/')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'Test123!',
            'user_type': 'user'
        }
    
    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')
    
    def test_register_user_existing_email(self):
        User.objects.create_user(email='test@example.com', password='Test123!')
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)
    
    def test_register_user_invalid_password(self):
        self.user_data['password'] = 'invalidpassword'
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)
    
    def test_register_user_missing_user_type(self):
        del self.user_data['user_type']
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

class UserListViewTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        request = self.factory.get('/')
        view = UserListView.as_view()

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, Response)

        # Add more positive test cases here

    def test_get_with_empty_users(self):
        request = self.factory.get('/')
        view = UserListView.as_view()

        # Clear all existing users
        User.objects.all().delete()

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, Response)
        self.assertEqual(len(response.data), 0)

        # Add more negative test cases here