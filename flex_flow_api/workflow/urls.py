from django.urls import path, include
from rest_framework.routers import DefaultRouter

from workflow.views import (
    WorkflowViewSet,
    NodeViewSet,
    EdgeViewSet,
    MessageViewSet,
    StatusView,
)

router = DefaultRouter()
router.register("", WorkflowViewSet)
router.register("(?P<workflow_pk>[^/.]+)/nodes", NodeViewSet, basename="node")
router.register("(?P<workflow_pk>[^/.]+)/edges", EdgeViewSet, basename="edge")
router.register(
    "(?P<workflow_pk>[^/.]+)/messages",
    MessageViewSet,
    basename="message"
)
router.register(
    "(?P<workflow_pk>[^/.]+)/messages/(?P<message_pk>[^/.]+)/status",
    StatusView,
    basename="status"
)

urlpatterns = [
    path('', include(router.urls)),
]
