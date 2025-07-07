from rest_framework_nested.routers import NestedDefaultRouter

from apps.tasks.urls import tasks_router

from .apps import ReviewsConfig
from .views import ReviewViewSet

app_name = ReviewsConfig.name


reviews_router = NestedDefaultRouter(tasks_router, "", lookup="task")
reviews_router.register("reviews", ReviewViewSet, "task-reviews")

urlpatterns = [
    *reviews_router.urls,
]
