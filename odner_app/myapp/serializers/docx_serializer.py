from rest_framework import serializers
from myapp.models import DOC # importazione modello (tabella DB) da serializzare

class DOCSerializer(serializers.ModelSerializer):
    class Meta:
        model = DOC
        fields = ('id', 'title', 'doc_file', 'docx_text_it', 'docx_text_en', 'txt_file_docx_it', 'txt_file_docx_en') # campi da serializzare