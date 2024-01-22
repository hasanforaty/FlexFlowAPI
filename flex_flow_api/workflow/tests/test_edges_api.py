from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Edge
from workflow.serializer import (EdgeSerializer, EdgeDetailSerializer)
from workflow.tests.utills import (
    create_workflow,
    create_user,
    create_node,
)


def get_edge_url(workflow_id):
    return reverse('edge-list', kwargs={'workflow_pk': workflow_id})


# def get_node_detail_url(workflow_id, edge_id):
#     return reverse(
#         'edge-detail',
#         kwargs={
#             'workflow_pk': workflow_id,
#             'pk': edge_id
#         }
#     )


class PublicWorkflowApiTests(TestCase):
    """Test the API without authentication"""

    def setUp(self):
        self.client = APIClient()
        user = create_user(
            email='user@example.com',
            password='user_pass'
        )
        self.workflow = create_workflow(user=user)

    def test_login_required(self):
        """Test that login is required for accessing this endpoint"""
        res = self.client.get(get_edge_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWorkflowApiTests(TestCase):
    """Test the authorized user API endpoint"""

    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='random_password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.workflow = create_workflow(self.user)
        self.nodes = [
            create_node(workflow=self.workflow, title="Node 1"),
            create_node(workflow=self.workflow, title="Node 2"),
            create_node(workflow=self.workflow, title="Node 3"),
            create_node(workflow=self.workflow, title="Node 4"),
            create_node(workflow=self.workflow, title="Node 5"),
            create_node(workflow=self.workflow, title="Node 6"),
        ]

    def test_retrieve_edge(self):
        """Test retrieving edge"""
        n1 = self.nodes[0]
        n2 = self.nodes[1]
        edge = Edge.objects.create(n_from=n1, n_to=n2, workflow=self.workflow)

        url = get_edge_url(self.workflow.id)
        serializer = EdgeDetailSerializer(Edge.objects.all(), many=True)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
