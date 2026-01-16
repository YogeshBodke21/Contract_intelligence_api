import faiss
import numpy as np
from Utils.embeddings import embed_text
from Utils.llm_response import call_llm_audit

def build_faiss_index(chunks):
    embeddings = np.array(
        [chunk.embedding for chunk in chunks],
        dtype="float32"
    )

    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity

    index.add(embeddings)
    print("index-- ", index)
    return index


def retrieve_chunks_for_risk(risk_query, index, chunks, top_k=5):
    query_embedding = embed_text(risk_query)
    query_vec = np.array([query_embedding], dtype="float32")
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)

    results = []
    for idx, score in zip(indices[0], scores[0]):
        results.append((chunks[idx], float(score)))

    return results


def audit_chunk_with_llm(chunk_text, risk_type):
    prompt = f"""
    You are a legal contract auditor.

    Risk type: {risk_type}

    Contract text:
    \"\"\"
    {chunk_text}
    \"\"\"

    Tasks:
    1. Decide if this text contains the risk.
    2. If yes, assign severity: LOW, MEDIUM, or HIGH.
    3. Extract the exact risky sentence(s).

    Return JSON ONLY in this format:
    {{
    "contains_risk": true/false,
    "severity": "LOW | MEDIUM | HIGH",
    "evidence": "quoted risky text"
    }}
    """
    llm_out = call_llm_audit(prompt)
    return llm_out


def retrieve_top_chunks(que, chunks):
    que_embedding = embed_text(que)
    que_vec = np.array([que_embedding], dtype="float32")
    index = build_faiss_index(chunks)

    faiss.normalize_L2(que_vec)
    top_k = 3
    scores, indices = index.search(que_vec, top_k)
    print("scores, indices", scores, indices)
    results = []
    for idx, score in zip(indices[0], scores[0]):
        results.append((chunks[idx], float(score)))

    return results


