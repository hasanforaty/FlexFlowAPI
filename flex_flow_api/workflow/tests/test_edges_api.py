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

    def test_retrieve_only_workflow_edge(self):
        """Test retrieving only edge of on specified workflow"""
        workflow_2 = create_workflow(self.user)
        node1 = create_node(workflow=workflow_2, title="Node")
        node2 = create_node(workflow=workflow_2, title="Node")
        edge = Edge.objects.create(n_from=node1, n_to=node2, workflow=workflow_2)
        url = get_edge_url(workflow_id=self.workflow.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = EdgeDetailSerializer(edge)
        self.assertNotIn(serializer.data, res.data)

    def test_create_edge(self):
        """Test creating edge"""
        n1 = self.nodes[0]
        n2 = self.nodes[1]
        payload = {
            "node_from": n1.id,
            'node_to': n2.id,
        }
        res = self.client.post(get_edge_url(self.workflow.id), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        edge = Edge.objects.filter(workflow_id=self.workflow.id)
        serializer = EdgeDetailSerializer(edge, many=True)
        self.assertEqual(edge.count(), 1)
        self.assertEqual(serializer.data[0].get('id'), res.data['id'])

    def test_create_edge_missmatch_node_and_workflow(self):
        """Test creating edge with miss matching node and workflow"""
        n1 = self.nodes[0]
        n2 = self.nodes[1]
        payload = {
            "node_from": n1.id,
            'node_to': n2.id,
        }
        workflow_2 = create_workflow(self.user)
        url = get_edge_url(workflow_id=workflow_2.id)
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_edge_mismatch_nodes(self):
        """Test creating edge with miss matching nodes"""
        n1 = self.nodes[0]
        workflow_2 = create_workflow(self.user)
        n2 = create_node(workflow=workflow_2)
        url = get_edge_url(workflow_id=workflow_2.id)
        payload = {
            "node_from": n1.id,
            'node_to': n2.id,
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
