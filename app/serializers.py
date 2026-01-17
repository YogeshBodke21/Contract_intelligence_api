from .models import Document, Contract_fields
from rest_framework import serializers



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class MultiPDFUploadSerializer(serializers.Serializer):
    file1 = serializers.FileField()
    file2 = serializers.FileField(required=False)
    file3 = serializers.FileField(required=False)

    
class Contract_fields_serializer(serializers.ModelSerializer):
    class Meta:
        model = Contract_fields
        fields = "__all__"

class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    document_id = serializers.IntegerField()

class AuditSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()