from rest_framework_nested.routers import NestedDefaultRouter

from apps.tasks.urls import tasks_router

from .apps import ProposalsConfig
from .views import ProposalViewSet

app_name = ProposalsConfig.name

proposals_router = NestedDefaultRouter(tasks_router, "", lookup="task")
proposals_router.register("proposals", ProposalViewSet, "task-proposals")

urlpatterns = [
    *proposals_router.urls,
]
