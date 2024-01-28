from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import MessageHolder, Edge
from workflow.tests.utills import (
    create_workflow,
    create_user,
    create_node,
    create_message
)


def _create_url(workflow_id, message_id):
    return reverse(
        'status-list',
        kwargs={
            'workflow_pk': workflow_id,
            'message_pk': message_id
        }
    )


class StatusAPITest(TestCase):
    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='random_password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.workflow = create_workflow(self.user)
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
        self.message = create_message(user=self.user, current_nod=self.n1)

    def test_approve_message(self):
        """Test approving a message"""
        url = _create_url(
            workflow_id=self.workflow.id,
            message_id=self.message.id)
        holder = MessageHolder.objects.filter(
            message_id=self.message.id,
        ).values_list('current_node', flat=True)
        pre_nodes = holder.all()
        payload = {
            'node': self.n1.id,
            'status': 'approved',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        holder = MessageHolder.objects.filter(
            message_id=self.message.id,
        ).values_list('current_node')
        changed_nodes = holder.all().distinct()
        for node in pre_nodes:
            self.assertNotIn(node, changed_nodes)

    def test_approve_message_History(self):
        """Test approving a message"""
        self.test_approve_message()
        url = reverse(
            'message-detail',
            kwargs={
                'workflow_pk': self.workflow.id,
                'pk': self.message.id,
            }
        ) + 'history/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
