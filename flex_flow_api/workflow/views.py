from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Workflow
from workflow.serializer import WorkflowSerializer
from workflow.permisions import IsOwnerOfObject


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated,IsOwnerOfObject]
    authentication_classes = [TokenAuthentication,]
