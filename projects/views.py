from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from .models import Project, Task, TeamMember
from .serializers import ProjectSerializer, TaskSerializer, TeamMemberSerializer
from rest_framework.exceptions import ValidationError 
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

import logging
from django.contrib.auth import get_user_model
User = get_user_model()
logger = logging.getLogger(__name__)

class ProjectListCreateView(generics.ListCreateAPIView):
    """
    View to list and create projects
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a project
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
    
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Task.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)  # <-- Automatically assign project


class TeamMemberListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return TeamMember.objects.filter(project_id=project_id)  # Only return members for this project

    def get_serializer_context(self):
        """Pass project instance to serializer context"""
        context = super().get_serializer_context()
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)
        print(f"DEBUG - Found Project: {project}")

        context["project"] = project  # Pass project in context
        return context

    def perform_create(self, serializer):
        project = self.get_serializer_context()["project"]

        user_id = self.request.data.get("user")
        if not user_id:
            raise ValidationError({"user": "User field is required."})

        # Ensure the user is not already a team member
        if TeamMember.objects.filter(project=project, user_id=user_id).exists():
            raise ValidationError({"error": "This user is already assigned to the project."})

        print(f"DEBUG - Adding user {user_id} to project {project}")

        # Save with the correct project instance
        serializer.save(project=project)


class UpdateTeamMemberRoleView(generics.UpdateAPIView):
    """Allows the project owner to update a team member's role."""
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeamMember.objects.all()

    def update(self, request, *args, **kwargs):
        print("UpdateTeamMemberRoleView was called!")  # Debugging step

        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        print(f"Project Owner: {project.owner}, Request User: {request.user}")
        
        if project.owner != request.user:
            print("Permission check failed!")  # Debugging
            raise PermissionDenied("Only the project owner can update roles.")

        team_member = get_object_or_404(TeamMember, project=project, user__id=self.kwargs["user_id"])
        print(f"Target Team Member: {team_member.user}")  # Debugging

        new_role = request.data.get("role")
        if new_role not in ["owner", "manager", "developer"]:
            return Response({"error": "Invalid role provided."}, status=status.HTTP_400_BAD_REQUEST)

        team_member.role = new_role
        team_member.save()
        return Response({"message": "Role updated successfully."}, status=status.HTTP_200_OK)



class DeleteTeamMemberView(generics.DestroyAPIView):
    """Allows the project owner to remove a team member from the project."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeamMember.objects.all()

    def delete(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])

        # Ensure only the owner can remove team members
        if project.owner != request.user:
            raise PermissionDenied("Only the project owner can remove team members.")

        # Get the team member to remove
        team_member = get_object_or_404(TeamMember, project=project, user__id=self.kwargs["user_id"])

        # Prevent owner from being removed
        if team_member.role == "owner":
            return Response({"error": "Owner cannot be removed from the project."}, status=status.HTTP_400_BAD_REQUEST)

        team_member.delete()
        return Response({"message": "Team member removed successfully."}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project, Task

from django.db.models import Count, Q

class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            # Aggregate project statistics
            project_counts = Project.objects.filter(owner=user).aggregate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                in_progress=Count("id", filter=Q(status="in_progress"))
            )

            # Aggregate task statistics
            task_counts = Task.objects.filter(project__owner=user).aggregate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                in_progress=Count("id", filter=Q(status="in_progress"))
            )

            # Calculate completion rates
            project_completion_rate = f"{(project_counts['completed'] / project_counts['total'] * 100):.0f}%" if project_counts['total'] else "0%"
            task_completion_rate = f"{(task_counts['completed'] / task_counts['total'] * 100):.0f}%" if task_counts['total'] else "0%"

            return Response({
                "projects": {
                    "total": project_counts["total"],
                    "completed": project_counts["completed"],
                    "in_progress": project_counts["in_progress"],
                    "completion_rate": project_completion_rate,
                },
                "tasks": {
                    "total": task_counts["total"],
                    "completed": task_counts["completed"],
                    "in_progress": task_counts["in_progress"],
                    "completion_rate": task_completion_rate,
                }
            })

        except Exception as e:
            return Response({"error": "Internal Server Error", "details": str(e)}, status=500)