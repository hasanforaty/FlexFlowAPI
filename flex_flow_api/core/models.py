from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a custom user"""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    objects = CustomUserManager()


class Workflow(models.Model):
    """Workflow model for our flexible workflows"""
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Node(models.Model):
    """Node model"""
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='nodes',
    )
    title = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Edge(models.Model):
    n_from = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='from+',
        blank=False
    )
    n_to = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='to+',
        blank=False,
    )
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        blank=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['n_from', 'n_to'],
                name="unique_edge"
            )
        ]

    def __str__(self):
        return f'{self.n_from} -> {self.n_to}'


class Message(models.Model):
    """Message model"""
    issuer = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'${self.issuer} -> ${self.message}'
