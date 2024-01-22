from django.urls import path, include
from rest_framework.routers import DefaultRouter

from workflow.views import WorkflowViewSet, NodeViewSet

router = DefaultRouter()
router.register("", WorkflowViewSet)
router.register("(?P<workflow_pk>[^/.]+)/nodes", NodeViewSet, basename="node")

urlpatterns = [
    path('', include(router.urls))
]
