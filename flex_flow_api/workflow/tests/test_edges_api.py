from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
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
