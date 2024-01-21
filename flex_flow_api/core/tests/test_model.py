
from django.test import TestCase
from django.contrib.auth import get_user_model


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
