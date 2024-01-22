from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

WORKFLOW_URL = reverse('workflow:workflow-list')


def create_user(**param):
    """Create and return new User"""
    user = get_user_model().objects.create_user(**param)
    return user


class PublicWorkflowApiTests(TestCase):
    """Test the API without authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for accessing this endpoint"""
        res = self.client.get(WORKFLOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

