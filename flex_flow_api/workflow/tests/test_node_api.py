from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Node, Workflow


# NODE_URL = reverse('node-list')


def get_node_url(workflow_id):
    return reverse('node-list', kwargs={'workflow_pk': workflow_id})


def get_node_list_url(node_id):
    return reverse('node-list', args=[node_id])


def create_workflow(user, **param):
    """Create workflow"""
    payload = {
        'title': 'Test Workflow',
        'description': 'testing workflow description'
    }
    payload.update(param)
    workflow = Workflow.objects.create(
        create_by=user,
        **payload,
    )
    return workflow


def create_user(**param):
    """Create and return new User"""
    user = get_user_model().objects.create_user(**param)
    return user


def create_node(workflow, **param):
    """Create and save Node"""
    payload = {
        'title': 'Test Title',
        'description': 'Test Description'
    }
    payload.update(param)
    return Node.objects.create(workflow=workflow, **param)


class PublicNodeApiTests(SimpleTestCase):
    """Test the publicly available API endpoint"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that Authentication is required for retrieving"""
        # res = self.client.get(NODE_URL)
        # self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        pass


class PrivateNodeApiTests(TestCase):
    """Test the authorized user API endpoint"""

    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='random_password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.workflow = create_workflow(self.user)

    def test_retrieve_nodes(self):
        """Test retrieving all the nodes"""
        create_node(workflow=self.workflow)
        res = self.client.get(get_node_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
