from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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
    create_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return self.title

    @classmethod
    def get_starting_nodes(cls, workflow):
        edges = Edge.objects.filter(workflow=workflow)
        node_form = set()
        node_to = set()
        for edge in edges:
            node_form.add(edge.n_from)
            node_to.add(edge.n_to)
        sd = node_form.symmetric_difference(node_to)
        starting_node = set()
        for node in sd:
            if node in node_form:
                starting_node.add(node)
        return starting_node

    @classmethod
    def get_next_nodes(cls, workflow, current_nod):
        edges = Edge.objects.filter(
            workflow=workflow,
            n_from=current_nod
        ).all()
        result = set()
        for edge in edges:
            result.add(edge.n_to)
        return result


class Node(models.Model):
    """Node model"""
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='nodes',
    )
    title = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255)
    is_finishing_node = models.BooleanField(default=False)

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
    issuer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'${self.issuer} -> ${self.message}'


class MessageHolder(models.Model):
    """Message holder model"""

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'pending'
        APPROVED = 'approved', 'approved'
        REJECTED = 'rejected', 'rejected'

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    current_node = models.ForeignKey(Node, on_delete=models.CASCADE)
    status = models.CharField(
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        max_length=16
    )

    def __str__(self):
        return (f"from : ${self.message.issuer}"
                f" message : ${self.message.message} "
                f"currently at ${self.current_node}"
                )


class History(models.Model):
    histories = models.JSONField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
