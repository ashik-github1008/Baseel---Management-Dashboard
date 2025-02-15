from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, TaskListCreateView, TeamMemberListCreateView, UpdateTeamMemberRoleView, DeleteTeamMemberView, DashboardAnalyticsView

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list-create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:project_id>/tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("<int:project_id>/team/", TeamMemberListCreateView.as_view(), name="team-list-create"),
    path("<int:project_id>/team/<int:user_id>/update/", UpdateTeamMemberRoleView.as_view(), name="update-team-role"),
    path("<int:project_id>/team/<int:user_id>/delete/", DeleteTeamMemberView.as_view(), name="delete-team-member"),
    path("dashboard/analytics/", DashboardAnalyticsView.as_view(), name="dashboard-analytics"),
]
