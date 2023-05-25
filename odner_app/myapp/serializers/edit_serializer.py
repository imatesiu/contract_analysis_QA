from rest_framework import serializers
from myapp.models import EditText # importazione modello (tabella DB) da serializzare

class EditSerializer(serializers.ModelSerializer):
    class Meta:
        model =  EditText
        fields = ('id', 'title', 'txt_file_edited') # campi da serializzare