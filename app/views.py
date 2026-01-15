from django.shortcuts import render
from .serializers import DocumentSerializer, Contract_fields_serializer
from .models import Document, Contract_fields, DocumentChunk
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import pdfplumber
from Utils.extraction import extract_fields_from_file
from Utils.embeddings import save_chunks_for_documents, embed_text
from Utils.similarity import cosine_similarity
from Utils.llm_response import call_llm
import json
# Create your views here.

@api_view(['POST'])
def ingest_view(request):
    files = request.FILES.getlist('files')
    print(files)
    docs = []
    for file in files:
        doc = Document.objects.create(file=file)
        try:
            with pdfplumber.open(doc.file.path) as pdf:
                file_text = "\n".join([ page.extract_text() or "" for page in pdf.pages])
                doc.text_content = file_text
                save_chunks_for_documents(file_text, doc.id)
                
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
    try:
        if doc:
            file_text = doc.text_content
            fields = extract_fields_from_file(file_text)
            print('fields--', fields)

            # Remove keys that don't exist on the model
            model_fields = {f.name for f in Contract_fields._meta.fields} #set comprehension
            clean_data = {k: v for k, v in fields.items() if k in model_fields and k != 'document'}

            contract, created = Contract_fields.objects.update_or_create(document = doc, defaults =clean_data) #(lookup, defaults)
            print('after query!!')
            serializer = Contract_fields_serializer(contract)
            return Response({"document": doc.id, 'fields':serializer.data, 'created':created}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"Error":  str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ask_question(request):
    que = request.data.get("question")
    doc = request.data.get("document_id")
    print(que, doc)
    embed_que = embed_text(que)
    #print(embed_que)
    try:
        chunks = DocumentChunk.objects.filter(document=doc)
        similarities = []
        for chunk in chunks:
            score = cosine_similarity(embed_que, chunk.embedding)
            similarities.append((score, chunk.text))
        similarities.sort(key=lambda x: x[0], reverse=True)
        top = 3
        top_chunks = similarities[:top]
        print(top_chunks)
        ans = call_llm(top_chunks, que)
        return Response({'question':que, "Answer": ans})
    except Exception as e:
        return Response({"Error" : str(e)})