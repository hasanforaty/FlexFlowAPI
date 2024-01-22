from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from core.models import Workflow, Node
from workflow.serializer import (
    WorkflowSerializer,
    NodeSerializer,
)
from workflow.permisions import IsOwnerOfObject


class NodeViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfObject]
    authentication_classes = [TokenAuthentication, ]
