from django.urls import path, include
from rest_framework.routers import DefaultRouter

from workflow.views import WorkflowViewSet, NodeViewSet, EdgeViewSet

router = DefaultRouter()
router.register("", WorkflowViewSet)
router.register("(?P<workflow_pk>[^/.]+)/nodes", NodeViewSet, basename="node")
router.register("(?P<workflow_pk>[^/.]+)/edges", EdgeViewSet, basename="edge")

urlpatterns = [
    path('', include(router.urls))
]
