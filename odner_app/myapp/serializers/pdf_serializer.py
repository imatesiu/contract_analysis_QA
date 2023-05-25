from rest_framework import serializers
from myapp.models import PDF # importazione modello (tabella DB) da serializzare

class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ('id', 'title', 'pdf_file', 'pdf_text_it', 'pdf_text_en', 'txt_file_pdf_it', 'txt_file_pdf_en') # campi da serializzare
