from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Message, Edge, MessageHolder
from workflow.serializer import MessageSerializer
from workflow.tests.utills import (
    create_workflow,
    create_user,
    create_node,
)


def _get_url(workflow_id):
    return reverse('message-list', kwargs={'workflow_pk': workflow_id})


class PublicMessageApiTests(TestCase):
    """Test the api without authentication"""

    def setUp(self):
        self.client = APIClient()
        user = create_user(
            email='user@example.com',
            password='user_pass'
        )
        self.workflow = create_workflow(user=user)

    def test_login_required(self):
        """Test that login is required for retrieving"""
        res = self.client.get(_get_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMessageApiTests(TestCase):
    """Test the api that need the authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='user_pass'
        )
        self.client.force_authenticate(user=self.user)
        self.workflow = create_workflow(user=self.user)
        self.n1 = create_node(workflow=self.workflow, title="Node 1")
        self.n2 = create_node(workflow=self.workflow, title="Node 2")
        self.n3 = create_node(workflow=self.workflow, title="Node 3")
        self.n4 = create_node(workflow=self.workflow, title="Node 4")
        self.edges = [
            Edge.objects.create(workflow=self.workflow, n_from=self.n1, n_to=self.n2),
            Edge.objects.create(workflow=self.workflow, n_from=self.n2, n_to=self.n3),
            Edge.objects.create(workflow=self.workflow, n_from=self.n3, n_to=self.n4),
        ]

    def test_creating_message(self):
        """Test creating message and it's handler"""
        text_message = 'Hello there'
        url = _get_url(self.workflow.id)
        payload = {
            'message': text_message
        }
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        holder = MessageHolder.objects.filter(
            current_node__workflow=self.workflow,
            message_id=response.data['id'],
        )
        self.assertEqual(holder.count(), 1)
        self.assertEqual(holder.first().message.message, text_message)
        self.assertEqual(holder.first().message.issuer, self.user)

    # def test_retrieve_messages(self):
    #     """Test retrieving all messages"""
    #     text_message = 'Hello there'
    #     Message.objects.create(
    #         issuer=self.user,
    #         message=text_message,
    #     )
    #     res = self.client.get(_get_url(self.workflow.id))
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 1)

    # def test_retrieve_messages_limited_to_workflow(self):
    #     """Test retrieving all messages limited to workflow"""
    #     text_message = 'Hello there'
    #     test_case = [
    #         Message.objects.create(
    #             issuer=self.user,
    #             message=text_message,
    #         ),
    #         Message.objects.create(
    #             issuer=self.user,
    #             message=text_message,
    #         )
    #     ]
    #     other_user = create_user(
    #         email='other_user@example.com',
    #         password='other_user_password'
    #     )
    #     create_workflow(user=other_user)
    #
    #     other_message = Message.objects.create(
    #         issuer=other_user,
    #         message=text_message,
    #     )
    #     res = self.client.get(_get_url(self.workflow.id))
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)
    #     serializer = MessageSerializer(other_message)
    #     self.assertNotIn(serializer.data, res.data)
