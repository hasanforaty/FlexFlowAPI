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

    def create(self, validated_data):
        user = self.context['request'].user
        workflow = Workflow.objects.create(
            create_by=user,
            **validated_data
        )
        return workflow
