from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Edge, MessageHolder, History
from workflow.serializer import (
    MessageSerializer,
    MessageDetailSerializer,
)
from workflow.tests.utills import (
    create_workflow,
    create_user,
    create_node,
    create_message,
)


def _get_url(workflow_id):
    return reverse('message-list', kwargs={'workflow_pk': workflow_id})


def _get_detail_url(workflow_id, message_id):
    return reverse(
        'message-detail',
        kwargs={
            'workflow_pk': workflow_id,
            'pk': message_id,
        }
    )


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
            Edge.objects.create(
                workflow=self.workflow,
                n_from=self.n1,
                n_to=self.n2,
            ),
            Edge.objects.create(
                workflow=self.workflow,
                n_from=self.n2,
                n_to=self.n3,
            ),
            Edge.objects.create(
                workflow=self.workflow,
                n_from=self.n3,
                n_to=self.n4,
            ),
        ]

    def test_creating_message(self):
        """Test creating a message and it's handler"""
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

    def test_retrieve_messages(self):
        """Test retrieving all messages"""
        create_message(user=self.user, current_nod=self.edges[0].n_from)
        res = self.client.get(_get_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_messages_limited_to_workflow(self):
        """Test retrieving all messages limited to workflow"""
        create_message(user=self.user, current_nod=self.edges[0].n_from),
        create_message(user=self.user, current_nod=self.edges[0].n_from),
        other_user = create_user(
            email='other_user@example.com',
            password='other_user_password'
        )
        other_workflow = create_workflow(user=other_user)
        n1 = create_node(workflow=other_workflow)
        n2 = create_node(workflow=other_workflow)
        Edge.objects.create(workflow=other_workflow, n_from=n1, n_to=n2)

        other_message = create_message(user=other_user, current_nod=n1)
        res = self.client.get(_get_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        serializer = MessageSerializer(other_message)
        self.assertNotIn(serializer.data, res.data)

    def test_retrieve_active_messages(self):
        """Test retrieving only active messages"""
        deactive_message = create_message(
            user=self.user,
            current_nod=self.edges[2].n_from,
            status=MessageHolder.StatusChoices.REJECTED
        )
        create_message(user=self.user, current_nod=self.edges[0].n_from)
        create_message(user=self.user, current_nod=self.edges[1].n_from)
        create_message(user=self.user, current_nod=self.edges[1].n_from)
        res = self.client.get(_get_url(self.workflow.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        serializer = MessageSerializer(deactive_message)
        self.assertNotIn(serializer.data, res.data)

    def test_retrieve_specific_message(self):
        """Test retrieving specific message"""
        msg = create_message(user=self.user, current_nod=self.edges[0].n_from)
        url = _get_detail_url(workflow_id=self.workflow.id, message_id=msg.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = MessageDetailSerializer(msg)
        self.assertEqual(serializer.data, res.data)

    def test_retrieve_message_history_mismatch(self):
        """Test retrieving messages history"""
        message = create_message(
            user=self.user,
            current_nod=self.edges[0].n_from
        )
        create_message(user=self.user, current_nod=self.edges[0].n_from)
        other_user = create_user(
            email='other_user@example.com',
            password='other_user_password'
        )
        other_workflow = create_workflow(user=other_user)
        n1 = create_node(workflow=other_workflow)
        n2 = create_node(workflow=other_workflow)
        Edge.objects.create(workflow=other_workflow, n_from=n1, n_to=n2)

        create_message(user=other_user, current_nod=n1)
        url = _get_detail_url(
            workflow_id=other_workflow.id,
            message_id=message.id) + "history/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_message_history(self):
        """Test retrieving message's History"""
        message = create_message(
            user=self.user,
            current_nod=self.edges[0].n_from
        )
        History.objects.create(
            histories={'message': message.message},
            content_object=message
        )
        url = _get_detail_url(
            workflow_id=self.workflow.id,
            message_id=message.id) + "history/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
