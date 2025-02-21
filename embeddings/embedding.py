import os
import json
import ssl
import io
import time
import numpy as np
import pandas as pd
import boto3
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra import ConsistencyLevel
from sentence_transformers import SentenceTransformer

def list_csv_keys(bucket_name, prefix, aws_region="us-east-1"):
    s3 = boto3.client('s3', region_name=aws_region)
    paginator = s3.get_paginator('list_objects_v2')
    keys = []
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".csv"):
                keys.append(key)
    return keys

def read_csv_from_s3(bucket_name, key, aws_region="us-east-1"):
    s3 = boto3.client('s3', region_name=aws_region)
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    data = obj['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(data))
    return df

def insert_openalex_data(session, df):
    query = """
        INSERT INTO research_data.openalex (id, title, abstract, publication_year)
        VALUES (?, ?, ?, ?)
    """
    prepared = session.prepare(query)
    for _, row in df.iterrows():
        session.execute(prepared, (
            row.get("id"),
            row.get("title"),
            row.get("abstract") if pd.notnull(row.get("abstract")) else None,
            int(row.get("publication_year")) if pd.notnull(row.get("publication_year")) else None
        ))

def insert_semantic_data(session, df):
    query = """
        INSERT INTO research_data.semantic_scholar (paperid, title, abstract, year, authors)
        VALUES (?, ?, ?, ?, ?)
    """
    prepared = session.prepare(query)
    for _, row in df.iterrows():
        paperid = row.get("paperid") if "paperid" in row else row.get("paperId")
        session.execute(prepared, (
            paperid,
            row.get("title"),
            row.get("abstract") if pd.notnull(row.get("abstract")) else None,
            int(row.get("year")) if pd.notnull(row.get("year")) else None,
            row.get("authors")
        ))

def fetch_openalex_documents(session):
    query = "SELECT id, title, abstract FROM openalex"
    rows = session.execute(query)
    docs = []
    for row in rows:
        text = ""
        if row.title:
            text += row.title
        if row.abstract:
            text += " " + row.abstract
        docs.append({'id': row.id, 'text': text})
    return docs

def fetch_semantic_documents(session):
    query = "SELECT paperid, title, abstract, authors FROM semantic_scholar"
    rows = session.execute(query)
    docs = []
    for row in rows:
        text = ""
        if row.title:
            text += row.title
        if row.abstract:
            text += " " + row.abstract
        if row.authors:
            text += " " + row.authors
        docs.append({'id': row.paperid, 'text': text})
    return docs

def compute_embeddings_for_docs(docs, model):
    texts = [doc['text'] for doc in docs]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return [(doc['id'], emb) for doc, emb in zip(docs, embeddings)]

def store_embeddings(session, embeddings, source):
    query = "INSERT INTO document_embeddings (id, source, embedding) VALUES (?, ?, ?)"
    prepared = session.prepare(query)
    for doc_id, emb in embeddings:
        emb_bytes = emb.tobytes()
        session.execute(prepared, (doc_id, source, emb_bytes))

def main():
    bucket_name = os.environ.get("BUCKET_NAME", "BUCKET_NAME")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")
    normalized_prefix = os.environ.get("NORMALIZED_PREFIX", "normalized/")
    keyspaces_endpoint = os.environ.get("KEYSPACES_ENDPOINT", "cassandra.us-east-2.amazonaws.com")
    service_username = os.environ.get("SERVICE_USERNAME")
    service_password = os.environ.get("SERVICE_PASSWORD")
    cert_path = os.environ.get("CERT_PATH", "/sf-class2-root.crt")

    print("Listing CSV files from S3...")
    csv_keys = list_csv_keys(bucket_name, normalized_prefix, aws_region)
    print("Found CSV files:", csv_keys)

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

    model = SentenceTransformer('all-MiniLM-L6-v2')

    openalex_docs = fetch_openalex_documents(session)
    semantic_docs = fetch_semantic_documents(session)
    print(f"Fetched {len(openalex_docs)} OpenAlex documents and {len(semantic_docs)} Semantic Scholar documents.")

    openalex_embeddings = compute_embeddings_for_docs(openalex_docs, model)
    semantic_embeddings = compute_embeddings_for_docs(semantic_docs, model)
    print("Computed embeddings for both data sources.")

    store_embeddings(session, openalex_embeddings, "openalex")
    store_embeddings(session, semantic_embeddings, "semantic")
    print("Stored all embeddings successfully.")

if __name__ == "__main__":
    main()
