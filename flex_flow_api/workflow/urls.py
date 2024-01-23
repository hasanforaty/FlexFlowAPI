from django.urls import path, include
from rest_framework.routers import DefaultRouter

from workflow.views import (
    WorkflowViewSet,
    NodeViewSet,
    EdgeViewSet,
    MessageViewSet,
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

urlpatterns = [
    path('', include(router.urls))
]
