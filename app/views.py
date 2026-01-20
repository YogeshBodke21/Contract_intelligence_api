from django.shortcuts import render
from .serializers import DocumentSerializer, Contract_fields_serializer, MultiPDFUploadSerializer, AskQuestionSerializer, AuditSerializer
from .models import Document, Contract_fields, DocumentChunk
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
import pdfplumber
from Utils.extraction import extract_fields_from_file
from Utils.embeddings import save_chunks_for_documents, embed_text
from Utils.similarity import cosine_similarity
from Utils.llm_response import call_llm, call_llm_stream
import json
from Utils.faiss import build_faiss_index, retrieve_chunks_for_risk, audit_chunk_with_llm, retrieve_top_chunks
from django.http import StreamingHttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema
from rest_framework import serializers



metrics = {
    "documents_ingested": Document.objects.count(),
    "questions_answered": 0,
    "audits_run": 0,
}



@extend_schema(
    tags=["Ingest the document Pdfs"],
    request=MultiPDFUploadSerializer,
    responses={200: serializers.DictField()}
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
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

@extend_schema(tags=["Extract the document details"])
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





@extend_schema(
        tags=['Ask Question'],
    request=AskQuestionSerializer,
    responses={200: serializers.DictField()},
    description="Ask a question based on a document"
)
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
        metrics['questions_answered'] += 1
        return Response({'Document_id':doc, 'question':que, "Answer": ans})
    except Exception as e:
        return Response({"Error" : str(e)})



RISK_QUERIES = {
    "AUTO_RENEWAL": "automatic renewal clause with short notice period",
    "UNLIMITED_LIABILITY": "unlimited liability clause",
    "BROAD_INDEMNITY": "broad indemnification obligations"
}

@extend_schema(
        tags=['Audit of given document'],
    request=AuditSerializer,
    responses={200: serializers.DictField()},
    description="Audit of document with resk analysis."
)
@api_view(["POST"])
def audit(request):
    document_id = request.data.get("document_id")

    if not document_id:
        return Response({"error": "document_id is required"}, status=400)

    # Fetch chunks
    chunks = list(DocumentChunk.objects.filter(document=document_id))

    if not chunks:
        return Response({"error": "No chunks found for document"}, status=404)
    # Build FAISS index
    index = build_faiss_index(chunks)
    unique_evidence = set()
    findings = []
    try:
        for risk_type, risk_query in RISK_QUERIES.items():
            retrieved_chunks = retrieve_chunks_for_risk(
                risk_query=risk_query,
                index=index,
                chunks=chunks,
                top_k=5
            )
            for chunk, score in retrieved_chunks:
                llm_result = audit_chunk_with_llm(chunk.text, risk_type)
                deserializer = json.loads(llm_result) #to convert it into python object - dict
                print("llm result", deserializer)
                if deserializer.get("contains_risk") is True:
                    if deserializer.get("evidence").strip() not in unique_evidence:
                        findings.append({
                            "risk": risk_type,
                            "severity": deserializer.get("severity"),
                            "document_id": document_id,
                            #"page": chunk.page or "",
                            #"char_range": [chunk.char_start, chunk.char_end],
                            "evidence": deserializer.get("evidence"),
                            "similarity_score": score
                        })
        metrics["audits_run"] += 1
        return Response({
            "document_id": document_id,
            "findings": findings
        }, status = status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            "error": str(e),
        }, status = status.HTTP_404_NOT_FOUND)


#for Stream
@extend_schema(
        tags=['Ask Question - stream answer'],
        request=AskQuestionSerializer,
        responses={200: serializers.DictField()},
        description="Ask a question based on a document"
)
@api_view(['POST'])
def ask_stream(request):
    try:
        #que = request.GET.get("question") for GET request
        que = request.data.get("question")
        doc = request.data.get("document_id")

        if not que or not doc:
            return StreamingHttpResponse(
                "data: Missing parameters\n\n",
                content_type="text/event-stream"
            )
        # Fetch chunks
        chunks = list(DocumentChunk.objects.filter(document=doc))
        #  Reusing SAME RAG logic
        top_chunks = retrieve_top_chunks(que, chunks)
        print("top_chunks-- ",top_chunks)
        def event_stream():
            try:
                for token in call_llm_stream(top_chunks, que):
                    yield f"data: {json.dumps({'token': token})}\n\n" #dict to json
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream"
        )
    except Exception as e:
        return Response({
            "error": str(e),
        }, status = status.HTTP_404_NOT_FOUND)

@extend_schema(
        tags=['Metrics of API']
)
@api_view(['GET'])
def get_metrics(request):
    return Response({"metrics":metrics}, status=status.HTTP_200_OK)