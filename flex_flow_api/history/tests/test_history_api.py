from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType

from core.models import History, Message
from history.serializers import HistorySerializer

HISTORY_URL = reverse('history:history-list')


class PublicHistoryApiTests(SimpleTestCase):
    """Test the API without authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for accessing this endpoint"""
        res = self.client.get(HISTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateHistoryApiTests(TestCase):
    """Test the authorized history API"""

    def setUp(self):
        self.user = user = get_user_model().objects.create_user(
            email='user@example.com',
            password='random_password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        payload = [
            {
                'message': 'Hello World!'
            }
        ]
        payload2 = [
            {
                'message': 'Hello World!'
            },
            {
                'message': 'Hello World!2'
            },
        ]
        self.message = Message.objects.create(
                    issuer=user,
                    message='Hello World!'
                )
        self.histories = [
            History.objects.create(
                histories=payload,
                content_object=self.message
            ),
            History.objects.create(
                histories=payload2,
                content_object=Message.objects.create(
                    issuer=user,
                    message='Hello World!2'
                )
            )
        ]

    def test_retrieve_history(self):
        """Test retrieving history for authenticated user"""

        res = self.client.get(HISTORY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(self.histories))
        for history in self.histories:
            serializer = HistorySerializer(history)
            self.assertIn(serializer.data, res.data)
