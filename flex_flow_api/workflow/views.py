from rest_framework.response import Response

from django.http import HttpResponseBadRequest
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from django.contrib.contenttypes.models import ContentType
from rest_framework import (
    viewsets, mixins)
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from core.models import (
    Workflow,
    Node,
    Edge, Message, MessageHolder,
    History,
)
from history.serializers import HistorySerializer
from workflow.permisions import IsOwnerOfObject
from workflow.serializer import (
    WorkflowSerializer,
    NodeSerializer,
    EdgeSerializer,
    EdgeDetailSerializer,
    MessageSerializer,
    MessageDetailSerializer,
    StatusSerializer,
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
                    current_node__workflow_id=workflow_id,
                    status=MessageHolder.StatusChoices.PENDING,
                ).values_list(
                    'message_id', flat=True
                )
            )

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ['retrieve']:
            return MessageDetailSerializer
        return self.serializer_class

    @action(detail=True, methods=['GET'], name='history')
    def history(self, request, *args, **kwargs):
        workflow_id = str(kwargs['workflow_pk'])
        messages_id = str(kwargs['pk'])
        message = MessageHolder.objects.filter(
            message_id=messages_id,
            current_node__workflow_id=workflow_id
        )
        if not message.exists():
            return HttpResponseBadRequest(content='Message not found')
        history = History.objects.filter(
            object_id=messages_id,
            content_type=ContentType.objects.get_for_model(Message)
        )
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data,)


@extend_schema_view(
    create=extend_schema(
        parameters=[
            OpenApiParameter(
                name='message_pk',
                type=OpenApiTypes.INT,
                description='id of the message you want to give state to ',
                required=True,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name='workflow_pk',
                type=OpenApiTypes.INT,
                description='id of the workflow you want change message in it',
                required=True,
                location=OpenApiParameter.PATH,
            ),
        ]
    )
)
class StatusView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = StatusSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, ]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
