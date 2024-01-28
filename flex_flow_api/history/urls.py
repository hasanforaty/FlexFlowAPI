from rest_framework import routers
from history.views import HistoryViewSet
from django.urls import path, include

router = routers.DefaultRouter()

router.register('', HistoryViewSet, basename='history')
app_name = 'history'
urlpatterns = [
    path('', include(router.urls))
]
