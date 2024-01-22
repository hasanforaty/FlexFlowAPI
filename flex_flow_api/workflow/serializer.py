from django.core.exceptions import BadRequest
from rest_framework import serializers
from core.models import (
    Workflow,
    Node,
    Edge
)
from rest_framework.exceptions import PermissionDenied


class EdgeSerializer(serializers.ModelSerializer):
    node_from = serializers.PrimaryKeyRelatedField(
        queryset=Node.objects.all(),
        source='n_from'
    )
    node_to = serializers.PrimaryKeyRelatedField(
        queryset=Node.objects.all(),
        source='n_to'
    )

    class Meta:
        model = Edge
        fields = [
            'id',
            'node_from',
            'node_to',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        workflow_id = self.context['view'].kwargs.get('workflow_pk')
        if not workflow_id:
            raise PermissionDenied(detail='No workflow_id was specified')
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        if not workflow:
            raise BadRequest(f"No workflow with id ${workflow_id} was found")
        for key in attrs.keys():
            if key in ['n_from', 'n_to']:
                if attrs[key].workflow.id != workflow.id:
                    raise BadRequest(
                        "Both node and workflow must be in same workflow"
                    )
        return attrs

    def create(self, validated_data):
        node_from = validated_data.pop('n_from')
        node_to = validated_data.pop('n_to')
        workflow_id = self.context['view'].kwargs.get('workflow_pk')
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        edge = Edge.objects.create(
            n_from=node_from,
            n_to=node_to,
            workflow=workflow,
        )
        edge.save()
        return edge


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
