from rest_framework import serializers
from users.models import CustomUser 
from rest_framework.exceptions import ValidationError
from .models import Project, Task, TeamMember

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["owner", "created_at"]

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'project']  # Ensure 'project' is listed
        extra_kwargs = {'project': {'required': False}}  # <-- This makes 'project' optional


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["id", "user", "role", "project"]
        read_only_fields = ["project"]

    def run_validation(self, data):
        """Override default validation to catch missing user earlier."""
        try:
            return super().run_validation(data)
        except serializers.ValidationError as e:
            # Customize error message if user does not exist
            if "user" in e.detail and isinstance(e.detail["user"], list):
                e.detail["user"] = ["User does not exist."]
            raise e

    def create(self, validated_data):
        project = self.context.get("project")
        print(f"DEBUG - Project in create(): {project}")

        if not project:
            raise serializers.ValidationError({"project": "This field is required."})

        validated_data["project"] = project
        return super().create(validated_data)
