from rest_framework import serializers
from .models import MessageModel

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'sender', 'recipient', 'listing', 'content', 'timestamp']
