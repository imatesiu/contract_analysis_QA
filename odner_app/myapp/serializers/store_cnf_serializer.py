from rest_framework import serializers
from myapp.models import Config

class CNFSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('id', 'title','json', 'json_str', 'language', 'entity_model')        