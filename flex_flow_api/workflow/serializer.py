from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import BadRequest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from core.models import (
    Workflow,
    Node,
    Edge,
    Message, MessageHolder, History,
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
            if key == 'n_from':
                if attrs[key].is_finishing_node:
                    raise BadRequest(
                        "can't create an edge from a fishing node"
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
            'is_finishing_node'
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


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'message',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        workflow_id = self.context['view'].kwargs.get('workflow_pk')
        if not workflow_id:
            raise PermissionDenied(detail='No workflow_id was specified')
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        if not workflow:
            raise BadRequest(f"No workflow with id ${workflow_id} was found")
        return attrs

    def create(self, validated_data):
        """Create a new message, put it in starting nodes"""
        user = self.context['request'].user
        workflow_id = self.context['view'].kwargs.get('workflow_pk')
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        start_node = Workflow.get_starting_nodes(workflow)
        message = Message.objects.create(
            issuer=user,
            message=validated_data['message']
        )
        for node in start_node:
            MessageHolder.objects.create(
                message=message,
                current_node=node
            )
        return message


class MessageDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message = serializers.CharField()
    current_node = serializers.ListField()

    def __init__(self, *args, **kwargs):
        # make sure only pending is shown
        current_nodes = MessageHolder.objects.filter(
            message_id=args[0].id,
            status=MessageHolder.StatusChoices.PENDING
        )
        node_list = []
        for holder in current_nodes:
            data = NodeSerializer(holder.current_node).data
            data['status'] = holder.status
            node_list.append(data)
        args[0].current_node = node_list
        super().__init__(*args, **kwargs)


class MessageHolderHistoryItem:
    def __init__(self, user, status, node):
        self.user = user
        self.status = status,
        self.nodeSerializer = node

    def serialize(self):
        return MessageHolderHistorySerializer(self)


class MessageHolderHistorySerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )
    timestamp = serializers.DateTimeField(default=timezone.now)
    status = serializers.CharField(max_length=255)
    node = serializers.CharField()

    def __init__(self, *args, **kwargs):
        args[0].node = args[0].nodeSerializer.data
        super().__init__(*args, **kwargs)


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    node = serializers.PrimaryKeyRelatedField(
        queryset=Node.objects.all()
    )

    def create(self, validated_data):
        """Create a new message, put it in starting nodes"""
        message_id = self.context['view'].kwargs.get('message_pk')
        workflow_id = self.context['view'].kwargs.get('workflow_pk')
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        messageHolder = MessageHolder.objects.get(
            message_id=message_id,
            current_node=validated_data['node'],
            status=MessageHolder.StatusChoices.PENDING
        )
        next_nodes = Workflow.get_next_nodes(
            workflow,
            messageHolder.current_node
        )
        history, created = History.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Message),
            object_id=message_id,
            defaults={
                'histories': []
            }
        )
        if validated_data['status'] == 'approved':
            for node in next_nodes:
                MessageHolder.objects.create(
                    message=messageHolder.message,
                    current_node=node
                )
            messageHolder.status = messageHolder.StatusChoices.APPROVED
        else:
            messageHolder.status = messageHolder.StatusChoices.REJECTED

        messageHolder.save()
        item = MessageHolderHistoryItem(
            user=self.context['request'].user,
            status=validated_data['status'],
            node=NodeSerializer(messageHolder.current_node)
        )
        historyserializer = item.serialize().data
        history.histories.append(historyserializer)
        history.save()
        if len(next_nodes) == 0 or validated_data['node'].is_finishing_node:
            #  we were in the last node , TODO
            # inform user about
            # if we are at ending node , find all of pending holder
            holders = MessageHolder.objects.filter(
                message_id=message_id,
                status=MessageHolder.StatusChoices.PENDING,
            )
            # change pending holder to final status
            for holder in holders:
                holder.status = messageHolder.status
                holder.save()

        return validated_data

    def validate(self, attrs):
        status = attrs['status']
        if status.lower() not in ['approved', 'rejected']:
            raise serializers.ValidationError(
                'Status must be approved or rejected'
            )
        return attrs
