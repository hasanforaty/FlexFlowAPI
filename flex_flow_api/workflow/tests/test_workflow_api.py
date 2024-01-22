from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Workflow
from workflow.serializer import WorkflowSerializer

WORKFLOW_URL = reverse('workflow:workflow-list')


def detail_url(workflow_id):
    return reverse(
        'workflow:workflow-detail',
        args=[workflow_id]
    )


def create_user(**param):
    """Create and return new User"""
    user = get_user_model().objects.create_user(**param)
    return user


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


class PublicWorkflowApiTests(SimpleTestCase):
    """Test the API without authentication"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for accessing this endpoint"""
        res = self.client.get(WORKFLOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWorkflowApiTests(TestCase):
    """Test the authorized endpoint of workflow"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='random_password',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_workflow(self):
        """Test retrieving a workflows"""
        create_workflow(user=self.user)
        res = self.client.get(WORKFLOW_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        workflow = Workflow.objects.all().order_by('-id')
        self.assertEqual(len(workflow), 1)
        serializer = WorkflowSerializer(workflow, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_get_workflows_detail(self):
        """Test retrieving a specific workflow"""
        workflow = create_workflow(user=self.user)
        serializer = WorkflowSerializer(workflow)
        res = self.client.get(detail_url(workflow.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_workflow(self):
        """Test creating workflows"""
        payload = {'title': 'test title', 'description': 'test description'}
        res = self.client.post(WORKFLOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        workflow = Workflow.objects.all().order_by('-id')
        self.assertEqual(len(workflow), 1)

    def test_partial_update_workflow(self):
        """Test updating workflow partially"""
        payload = {'title': 'test title'}
        workflow = create_workflow(user=self.user)
        res = self.client.patch(detail_url(workflow.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        workflow.refresh_from_db()
        self.assertEqual(workflow.title, payload['title'])

    def test_update_workflow(self):
        """Test updating a workflow completely"""
        payload = {'title': 'test title', 'description': 'test description'}
        workflow = create_workflow(user=self.user)
        res = self.client.patch(
            detail_url(workflow.id),
            payload,
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        workflow.refresh_from_db()
        self.assertEqual(workflow.title, payload['title'])
        self.assertEqual(workflow.description, payload['description'])

    def test_update_user_returns_error(self):
        """Test updating user by workflow result in error"""
        workflow = create_workflow(user=self.user)
        payload = {
            'create_by': create_user(
                email='user2@example.com',
                password='password'
            )
        }
        url = detail_url(workflow.id)
        self.client.patch(url, payload)
        workflow.refresh_from_db()
        self.assertEqual(workflow.create_by, self.user)

    def test_delete_workflow(self):
        """Test deleting a workflow"""
        workflow = create_workflow(user=self.user)
        res = self.client.delete(detail_url(workflow.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        workflows = Workflow.objects.all()
        self.assertEqual(len(workflows), 0)

    def test_deleting_workflow_of_other_user(self):
        """Test deleting workflow of other user give error message"""
        user = create_user(
            email='custom@example.com',
            password='password_custom',)

        workflow = create_workflow(user=user)
        res = self.client.delete(detail_url(workflow))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Workflow.objects.filter(id=workflow.id).exists())

    def test_retrieve_other_user_workflow(self):
        """Test retrieving another user workflow"""
        user1 = create_user(
            email='custom@example.com',
            password='password_custom',
        )
        user2 = create_user(
            email='custom2@example.com',
            password='password_custom2',
        )
        workflow1 = create_workflow(user=user1)
        workflow2 = create_workflow(user=user2)
        serializer1 = WorkflowSerializer(workflow1)
        serializer2 = WorkflowSerializer(workflow2)
        res = self.client.get(WORKFLOW_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    # def test_updating_workflow_of_other_user(self):
    #     """Test updating workflow of other user give error message"""
    #     user1 = create_user(
    #     email='custom@example.com',
    #     password='password_custom',
    #     )
    #     workflow1 = create_workflow(user=user1)
    #     res = self.client.patch(
    #     detail_url(workflow1.id),
    #     {'name': 'new_name'},
    #     format='json',
    #     )
    #     self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
