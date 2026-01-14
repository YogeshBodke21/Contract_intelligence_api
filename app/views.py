from django.shortcuts import render
from .serializers import DocumentSerializer
from .models import Document
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import pdfplumber
from Utils.extraction import extract_fields_from_file
# Create your views here.

@api_view(['POST'])
def ingest_view(request):
    files = request.FILES.getlist('files')
    docs = []
    for file in files:
        doc = Document.objects.create(file=file)
        try:
            with pdfplumber.open(doc.file.path) as pdf:
                file_text = "\n".join([ page.extract_text() or "" for page in pdf.pages])
                doc.text_content = file_text
            doc.save()
        except:
            doc.text_content = ""
            doc.save()
        docs.append(doc.id)
    print(docs)
    return Response({"Document IDs": docs },status=status.HTTP_201_CREATED)

@api_view(['POST'])
def extract_details(request, pk):
    print("------>", pk)
    try:
        doc = Document.objects.get(id=pk)
    except:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

    if doc:
        file_text = doc.text_content
        fields = extract_fields_from_file(file_text)
        return Response({pk: fields}, status=status.HTTP_200_OK)
