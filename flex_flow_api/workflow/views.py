from rest_framework import (
    viewsets, mixins, )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from core.models import (
    Workflow,
    Node,
    Edge, Message, MessageHolder,
)
from workflow.permisions import IsOwnerOfObject
from workflow.serializer import (
    WorkflowSerializer,
    NodeSerializer,
    EdgeSerializer,
    EdgeDetailSerializer,
    MessageSerializer,
)


class EdgeViewSet(
    viewsets.ModelViewSet
):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["retrieve", 'list']:
            return EdgeDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        workflow_id = str(self.kwargs['workflow_pk'])
        if workflow_id:
            return Edge.objects.filter(workflow_id=workflow_id)
        # return Edge.objects.all()


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


class MessageViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, ]

    def get_queryset(self):
        workflow_id = str(self.kwargs['workflow_pk'])
        if workflow_id:
            return Message.objects.filter(
                id__in=MessageHolder.objects.filter(
                    current_node__workflow_id=workflow_id
                ).values_list(
                    'message_id', flat=True
                )
            )



