from rest_framework.routers import DefaultRouter

from .apps import TasksConfig
from .views import TaskViewSet

app_name = TasksConfig.name

task_router = DefaultRouter()
task_router.register("", TaskViewSet, "task")

urlpatterns = [
    *task_router.urls,
]
