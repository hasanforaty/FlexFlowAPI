from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from core.models import (
    Workflow, Node, Edge, Message, MessageHolder, History
)


class ModelTests(TestCase):
    """Test model of core application."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email instead of username."""
        email = "user@example.com"
        password = "random_password"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        test_cases = [
            ['teSt@examPle.com', 'teSt@example.com'],
            ['TEST@EXAMPLE.COM', 'TEST@example.com'],
            ['Test@Example.Com', 'Test@example.com']
        ]
        for email, expected_email in test_cases:
            user = get_user_model().objects.create_user(
                email=email, password='password'
            )
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test creating a new user with no email to raise an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'random_password')

    def test_create_new_superuser(self):
        """Test creating and saving new superuser"""
        email = 'test@example.com'
        user = (get_user_model().objects.
                create_superuser(email=email, password='password'))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, email)

    def test_create_workflow(self):
        """Test creating a workflow"""
        user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        workflow = Workflow.objects.create(
            title='Test Workflow',
            description='testing workflow description',
            create_by=user
        )
        self.assertEqual(str(workflow), workflow.title)

    def test_create_Node(self):
        """Test creating Node """
        user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        workflow = Workflow.objects.create(
            title='Test Workflow',
            description='testing workflow description',
            create_by=user
        )
        node = Node.objects.create(
            title='Test Node',
            description='Num 1',
            workflow=workflow
        )
        self.assertEqual(str(node), node.title)

    def test_create_node_edge(self):
        """Test creating Node connection between two Node"""
        user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        workflow = Workflow.objects.create(
            title='Test Workflow',
            description='testing workflow description',
            create_by=user
        )
        node = Node.objects.create(
            title='Test Node',
            description='Num 1',
            workflow=workflow
        )
        node2 = Node.objects.create(
            title='Test Node2',
            description='Num 2',
            workflow=workflow
        )
        edge = Edge.objects.create(
            n_from=node, n_to=node2,
            workflow=workflow
        )
        self.assertEqual(str(edge), f'{node.title} -> {node2.title}')

    def test_create_repeated_edge_raise_error(self):
        """Test creating duplicate edge raises error"""
        user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        workflow = Workflow.objects.create(
            title='Test Workflow',
            description='testing workflow description',
            create_by=user
        )
        node = Node.objects.create(
            title='Test Node',
            description='Num 1',
            workflow=workflow
        )
        node2 = Node.objects.create(
            title='Test Node2',
            description='Num 2',
            workflow=workflow
        )
        Edge.objects.create(
            n_from=node, n_to=node2,
            workflow=workflow
        )
        with self.assertRaises(IntegrityError):
            Edge.objects.create(
                n_from=node, n_to=node2,
                workflow=workflow
            )

    def test_create_message_model(self):
        """Test creating message model"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_password',
        )
        message = Message.objects.create(
            issuer=user,
            message='test message'
        )
        self.assertEqual(message.issuer, user)
        self.assertEqual(message.message, 'test message')

    def test_create_message_holder(self):
        """Test creating message holder"""
        user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        workflow = Workflow.objects.create(
            title='Test Workflow',
            description='testing workflow description',
            create_by=user
        )
        node = Node.objects.create(
            title='Test Node',
            description='Num 1',
            workflow=workflow
        )
        message = Message.objects.create(
            issuer=user,
            message='test message'
        )
        holder = MessageHolder.objects.create(
            current_node=node,
            message=message
        )
        self.assertEqual(
            holder.current_node,
            node
        )
        self.assertEqual(
            str(holder),
            f"from : ${message.issuer}"
            f" message : ${message.message} "
            f"currently at ${holder.current_node}"
        )

    def test_create_history(self):
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_password',
        )
        message = Message.objects.create(
            issuer=user,
            message='test message'
        )
        payload = {
            'message': message.message,
            'issuer': message.issuer.id,
        }
        history = History.objects.create(
            histories=payload,
            content_object=message,
        )
        self.assertEqual(history.content_object, message)
