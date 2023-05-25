from rest_framework import serializers
from myapp.models import XLSX # importazione modello (tabella DB) da serializzare


class XLSXSerializer(serializers.ModelSerializer):
    class Meta:
        model = XLSX
        fields = ('id', 'title', 'xlsx_file', 'xlsx_text_it', 'xlsx_text_en', 'txt_file_xlsx_it', 'txt_file_xlsx_en') # campi da serializzare
