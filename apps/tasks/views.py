from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsClient

from .models import Task
from .permissions import IsTaskOpen, IsTaskOwner
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.action in ["create"]:
            permissions += [IsClient()]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsTaskOpen(), IsTaskOwner()]
        return permissions

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
