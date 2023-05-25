from rest_framework import serializers
from myapp.models import NER

class NERserializer(serializers.ModelSerializer):
    class Meta:
        model = NER
        fields = ('id', 'title', 'raw_file','jsonDict', 'jsonNER', 'language' , 'jsondict_str', 'jsonner_str', 'entity_model_current')