from app.models import Document, DocumentChunk
#from openai import OpenAI
from google.ai import generativelanguage as gl
from sentence_transformers import SentenceTransformer


# Small, fast, excellent for RAG
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str):
    return model.encode(text).tolist()

#############################


def save_chunks_for_documents(text, doc, chunk_size=30):
    if not text:
        return []
    
    words = text.split()
    dict_ch = {}
    document_instance = Document.objects.get(id=doc)
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    for idx, chunk_text in enumerate(chunks):
        print("\n",idx, chunk_text)
        embedded_response = embed_text(chunk_text)
        try:
            print("inside try")
            DocumentChunk.objects.update_or_create(
                document = document_instance,
                chunk_id = int(idx) + 1,
                defaults = {
                    "text" : chunk_text,
                    "embedding" : embedded_response,
                    "page_number" : None
                }
            )
            print('chunk saved!')
            dict_ch[idx] = embedded_response
        except Exception as e:
            print(e)


    #print("Embedded text --->", dict_ch)



# text = '''
# Title: Master Services Agreement between Gamma Solutions and Delta Partners
# Document ID: 2
# Parties:
# - Party A: Gamma Solutions
# - Party B: Delta Partners
# Effective Date: 2026-02-01
# Term: 24 months
# Governing Law: California
# Payment Terms: Invoices payable within 30 days
# Termination: Either party may terminate with 60 days written notice
# Auto Renewal: Automatically renews for 12 months unless canceled 30 days prior
# Confidentiality: All confidential info shall be protected for 5 years
# Indemnity: Party B indemnifies Party A against all claims arising from services
# Liability Cap: {"amount": 1000000, "currency": "USD"}
# Signatories:
# - Name: Carol White, Title: CEO (Gamma Solutions)
# - Name: Dave Brown, Title: CFO (Delta Partners)'''
# save_chunks_for_documents(text, 1)