from rest_framework.routers import DefaultRouter

from .apps import TasksConfig
from .views import TaskViewSet

app_name = TasksConfig.name

tasks_router = DefaultRouter()
tasks_router.register("", TaskViewSet, "task")

urlpatterns = [
    *tasks_router.urls,
]
