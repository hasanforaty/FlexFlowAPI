from rest_framework import serializers

from core.models import History


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'
        read_only_fields = [
            'id'
        ]
