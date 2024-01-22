from django.urls import path, include
from rest_framework.routers import DefaultRouter

from workflow.views import WorkflowViewSet

router = DefaultRouter()
router.register("workflow", WorkflowViewSet)


app_name = 'workflow'
urlpatterns = [
    path('', include(router.urls))
]
