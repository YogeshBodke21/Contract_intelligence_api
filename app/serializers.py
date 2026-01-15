from .models import Document, Contract_fields
from rest_framework import serializers



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class Contract_fields_serializer(serializers.ModelSerializer):
    class Meta:
        model = Contract_fields
        fields = "__all__"