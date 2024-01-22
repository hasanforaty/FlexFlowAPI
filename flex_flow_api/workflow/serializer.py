from rest_framework import serializers
from core.models import (
    Workflow,
    Node,
    Edge
)


class EdgeSerializer(serializers.ModelSerializer):
    node_from = serializers.CharField()
    node_to = serializers.CharField()

    class Meta:
        model = Edge
        fields = [
            'id',
            'node_from',
            'node_to',
        ]
        read_only_fields = ['id']


class EdgeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        fields = [
            'id',
            'n_to',
            'n_from',
        ]
        read_only_fields = ['id', 'n_to', 'n_from']


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = [
            'id',
            'title',
            'description',
        ]
        read_only_fields = ['id', ]

    def create(self, validated_data):
        workflow_pk = self.context['view'].kwargs['workflow_pk']
        workflow = Workflow.objects.get(pk=workflow_pk)
        node = Node.objects.create(workflow=workflow, **validated_data)
        node.save()
        return node


class WorkflowSerializer(serializers.ModelSerializer):
    nodes = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Workflow
        fields = [
            'id',
            'title',
            'description',
            'nodes'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('nodes', None)
        workflow = Workflow.objects.create(
            create_by=user,
            **validated_data
        )
        return workflow
