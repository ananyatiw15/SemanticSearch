import os
import json
import boto3
import pandas as pd
import io
import ssl
from cassandra import ConsistencyLevel
import time
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_REQUIRED
from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider

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
        title = row.get("title") if pd.notnull(row.get("title")) else None
        abstract = row.get("abstract") if pd.notnull(row.get("abstract")) else None
        year = int(row.get("year")) if pd.notnull(row.get("year")) else None
        authors = row.get("authors") if pd.notnull(row.get("authors")) else None

        session.execute(prepared, (paperid, title, abstract, year, authors))


def main():
    bucket_name = os.environ.get("BUCKET_NAME", "BUCKET_NAME")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")
    normalized_prefix = os.environ.get("NORMALIZED_PREFIX", "normalized/")
    keyspaces_endpoint = os.environ.get("KEYSPACES_ENDPOINT", "cassandra.us-east-2.amazonaws.com")
    service_username = os.environ.get("SERVICE_USERNAME")
    service_password = os.environ.get("SERVICE_PASSWORD")
    cert_path = os.environ.get("CERT_PATH", "/var/task/sf-class2-root.crt")

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

    for key in csv_keys:
        print("Processing file:", key)
        df = read_csv_from_s3(bucket_name, key, aws_region)
        if "openalex_data.csv" in key:
            print("Inserting OpenAlex data...")
            insert_openalex_data(session, df)
        elif "semantic_data.csv" in key:
            print("Inserting Semantic Scholar data...")
            insert_semantic_data(session, df)
        else:
            print(f"Unknown file type for key {key}; skipping.")
    print("All data insertion complete.")

def lambda_handler(event, context):
    try:
        main()
        return {
            'statusCode': 200,
            'body': json.dumps('All CSV data inserted successfully into AWS Keyspaces!')
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
