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
   viewsets.ModelViewSet
):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def get_queryset(self):
        workflow_id = str(self.kwargs['workflow_pk'])
        if workflow_id:
            return Node.objects.filter(workflow_id=workflow_id)
        return Node.objects


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfObject]
    authentication_classes = [TokenAuthentication, ]
