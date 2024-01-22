from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Node
from workflow.serializer import NodeSerializer
from workflow.tests.utills import (
    create_workflow,
    create_user,
    create_node,
)


# NODE_URL = reverse('node-list')


def get_node_url(workflow_id):
    return reverse('node-list', kwargs={'workflow_pk': workflow_id})


def get_node_detail_url(workflow_id, node_id):
    return reverse(
        'node-detail',
        kwargs={
            'workflow_pk': workflow_id,
            'pk': node_id
        }
    )


def get_node_list_url(node_id):
    return reverse('node-list', args=[node_id])


class PublicNodeApiTests(TestCase):
    """Test the publicly available API endpoint"""

    def setUp(self):
        self.client = APIClient()
        user = create_user(
            email='user@example.com',
            password='user_pass'
        )
        self.workflow = create_workflow(user=user)

    def test_login_required(self):
        """Test that Authentication is required for retrieving"""
        res = self.client.get(get_node_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_retrieve_only_workflow_node(self):
        """Test retrieving only node of specific workflow"""
        test_case = [
            create_node(self.workflow),
            create_node(self.workflow),
        ]
        other_user = create_user(
            email='other_user@example.com',
            password='other_user_password'
        )
        other_workflow = create_workflow(user=other_user)
        create_node(workflow=other_workflow)

        res = self.client.get(get_node_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        serializer = NodeSerializer(test_case, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_create_node(self):
        """Test creating node"""
        payload = {'title': 'test title', 'description': 'test description'}
        res = self.client.post(get_node_url(self.workflow.id), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        nodes = Node.objects.filter(workflow_id=self.workflow.id)
        self.assertEqual(nodes.count(), 1)

    def test_update_node(self):
        """Test updating a node"""
        node = create_node(self.workflow)
        payload = {
            'title': 'test title2',
            'description': 'test34'
        }
        res = self.client.put(
            get_node_detail_url(
                self.workflow.id,
                node_id=node.id
            ), payload
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK
        )
        node.refresh_from_db()
        self.assertEqual(node.title, payload['title'])
        self.assertEqual(
            node.description,
            payload['description'],
        )
        self.assertEqual(
            node.workflow_id,
            self.workflow.id,
        )

    def test_update_partial_node(self):
        """Test updating a node partially"""
        node = create_node(self.workflow)
        payload = {'title': 'test'}
        res = self.client.patch(
            get_node_detail_url(
                self.workflow.id,
                node_id=node.id
            ),
            payload,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        node.refresh_from_db()
        self.assertEqual(node.title, payload['title'])
        self.assertEqual(node.workflow_id, self.workflow.id)

    def test_delete_node(self):
        """Test deleting a node"""
        node = create_node(self.workflow)
        res = self.client.delete(
            get_node_detail_url(
                node_id=node.id,
                workflow_id=self.workflow.id
            )
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertNotIn(
            node,
            Node.objects.filter(workflow_id=self.workflow),
        )

    def test_get_node_details(self):
        """Test getting node details"""
        node = create_node(self.workflow)
        res = self.client.get(
            get_node_detail_url(
                workflow_id=self.workflow.id,
                node_id=node.id
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        s = NodeSerializer(node)
        self.assertEqual(s.data, res.data)
