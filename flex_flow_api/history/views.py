from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from core.models import History
from history.serializers import HistorySerializer


class HistoryViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def get_serializer_class(self):
        if self.action == "list":
            return HistorySerializer
