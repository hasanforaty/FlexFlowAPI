from core.models import (
    Workflow,
    Node, Message, MessageHolder,
)
from django.contrib.auth import get_user_model


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


def create_user(**param):
    """Create and return new User"""
    user = get_user_model().objects.create_user(**param)
    return user


def create_node(workflow, is_finishing_nod=False, **param):
    """Create and save Node"""
    payload = {
        'title': 'Test Title',
        'description': 'Test Description'
    }
    payload.update(param)
    return Node.objects.create(
        workflow=workflow,
        is_finishing_node=is_finishing_nod,
        **param
    )


def create_message(
        user,
        current_nod,
        status=MessageHolder.StatusChoices.PENDING,
        **param
):
    payload = {
        'message': 'Test Message',
    }
    payload.update(param)
    message = Message.objects.create(
        issuer=user,
        **payload,
    )
    MessageHolder.objects.create(
        message=message,
        current_node=current_nod,
        status=status
    )
    return message
