from django.urls import path, include
from rest_framework.routers import DefaultRouter

from workflow.views import WorkflowViewSet, NodeViewSet

router = DefaultRouter()
router.register("workflow", WorkflowViewSet)
router.register("node", NodeViewSet)


app_name = 'workflow'
urlpatterns = [
    path('', include(router.urls))
]
