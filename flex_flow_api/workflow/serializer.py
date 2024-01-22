from rest_framework import serializers

from core.models import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = [
            'id',
            'title',
            'description',
        ]
        read_only_fields = ['id']
