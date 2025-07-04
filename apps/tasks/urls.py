from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .apps import TasksConfig
from .views import ProposalViewSet, TaskViewSet

app_name = TasksConfig.name

tasks_router = DefaultRouter()
tasks_router.register("tasks", TaskViewSet, "task")

proposals_router = NestedDefaultRouter(tasks_router, "tasks", lookup="task")
proposals_router.register("proposals", ProposalViewSet, "task-proposals")

urlpatterns = [
    *tasks_router.urls,
    *proposals_router.urls,
]
