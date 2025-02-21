import os
import ssl
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra import ConsistencyLevel
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm
import uvicorn
import boto3
import pandas as pd
import io
import faiss

app = FastAPI()

faiss_index = None
docs_metadata = None
embedding_model = None
cassandra_session = None

class QueryRequest(BaseModel):
    query: str
    k: int = 5

def setup_cassandra_session():
    keyspaces_endpoint = os.environ.get("KEYSPACES_ENDPOINT", "cassandra.us-east-2.amazonaws.com")
    service_username = os.environ.get("SERVICE_USERNAME")
    service_password = os.environ.get("SERVICE_PASSWORD")
    cert_path = os.environ.get("CERT_PATH", "/sf-class2-root.crt")

    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cert_path)
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = True
    original_wrap_socket = ssl_context.wrap_socket
    def custom_wrap_socket(sock, server_side=False, do_handshake_on_connect=True,
                           suppress_ragged_eofs=True, server_hostname=None, *args, **kwargs):
        return original_wrap_socket(sock, server_side, do_handshake_on_connect,
                                    suppress_ragged_eofs, server_hostname=keyspaces_endpoint, *args, **kwargs)
    ssl_context.wrap_socket = custom_wrap_socket

    auth_provider = PlainTextAuthProvider(username=service_username, password=service_password)
    cluster = Cluster(
        [keyspaces_endpoint],
        port=9142,
        ssl_context=ssl_context,
        auth_provider=auth_provider
    )
    session = cluster.connect()
    session.set_keyspace("research_data")
    session.default_consistency_level = ConsistencyLevel.LOCAL_QUORUM
    return session

def fetch_all_document_embeddings(session):
    query = "SELECT id, source, embedding FROM document_embeddings"
    rows = session.execute(query)
    docs = []
    for row in rows:
        emb = np.frombuffer(row.embedding, dtype=np.float32)
        docs.append({
            'id': row.id,
            'source': row.source,
            'embedding': emb
        })
    return docs

def build_faiss_index(docs):
    if not docs:
        raise ValueError("No documents available for indexing.")
    dimension = docs[0]['embedding'].shape[0]
    embeddings = []
    for doc in docs:
        norm_emb = doc['embedding'] / (norm(doc['embedding']) + 1e-10)
        embeddings.append(norm_emb)
    embeddings = np.stack(embeddings).astype('float32')
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return index

def lookup_document_details(session, doc_id, source):
    if source.lower() == "openalex":
        query = "SELECT id, title, abstract FROM openalex WHERE id = %s"
    elif source.lower() == "semantic":
        query = "SELECT paperid, title, abstract, authors FROM semantic_scholar WHERE paperid = %s"
    else:
        return {}

    row = session.execute(query, (doc_id,)).one()
    if row:
        if source.lower() == "openalex":
            details = {
                "id": row.id,
                "title": row.title,
                "abstract": row.abstract
            }
        else:
            details = {
                "paperid": row.paperid,
                "title": row.title,
                "abstract": row.abstract,
                "authors": row.authors
            }
        return { k: v for k, v in details.items() if v is not None }
    return {}


def retrieve_top_k(query_embedding, index, docs, k=5):
    query_embedding = query_embedding / (norm(query_embedding) + 1e-10)
    query_embedding = np.expand_dims(query_embedding.astype('float32'), axis=0)
    distances, indices = index.search(query_embedding, k)
    results = []
    for i in indices[0]:
        doc = docs[i]
        results.append({
            'id': doc['id'],
            'source': doc['source']
        })
    return results

@app.on_event("startup")
def startup_event():
    global cassandra_session, docs_metadata, faiss_index, embedding_model
    cassandra_session = setup_cassandra_session()
    docs_metadata = fetch_all_document_embeddings(cassandra_session)
    print(f"Fetched {len(docs_metadata)} documents from Keyspaces.")
    faiss_index = build_faiss_index(docs_metadata)
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Startup complete: FAISS index and embedding model loaded.")

@app.post("/query")
def query_documents(req: QueryRequest):
    if embedding_model is None or faiss_index is None or docs_metadata is None:
        raise HTTPException(status_code=500, detail="Service not fully initialized.")

    total_docs = len(docs_metadata)
    if req.k > total_docs:
        k = min(10, total_docs)
    else:
        k = req.k

    query_embedding = embedding_model.encode(req.query, convert_to_numpy=True)
    top_docs = retrieve_top_k(query_embedding, faiss_index, docs_metadata, k=k)

    detailed_results = []
    for doc in top_docs:
        details = lookup_document_details(cassandra_session, doc['id'], doc['source'])
        detailed_results.append(details)

    return {"results": detailed_results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
