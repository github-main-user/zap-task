from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from apps.proposals.views import ProposalViewSet
from apps.reviews.views import ReviewViewSet

from .apps import TasksConfig
from .views import TaskViewSet

app_name = TasksConfig.name

tasks_router = DefaultRouter()
tasks_router.register("", TaskViewSet, "task")

proposals_router = NestedDefaultRouter(tasks_router, "", lookup="task")
proposals_router.register("proposals", ProposalViewSet, "task-proposals")

reviews_router = NestedDefaultRouter(tasks_router, "", lookup="task")
reviews_router.register("reviews", ReviewViewSet, "task-reviews")


urlpatterns = [
    *tasks_router.urls,
    *proposals_router.urls,
    *reviews_router.urls,
]
