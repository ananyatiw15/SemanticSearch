import os
import json
import requests
import boto3
import time
import pandas as pd
from io import StringIO

def fetch_openalex_data(query, per_page=20):
    url = "https://api.openalex.org/works"
    params = {
        'filter': f'title.search:{query}',
        'per_page': per_page
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_semantic_scholar_data(query, limit=20, retries=3, backoff=2):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'paperId,title,abstract,authors,year'
    }
    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 429:
            print(f"Rate limit hit. Retrying in {backoff} seconds...")
            time.sleep(backoff)
            backoff *= 2
        else:
            response.raise_for_status()
            return response.json()
    response.raise_for_status()

def reconstruct_abstract(abstract_inverted_index):
    if not abstract_inverted_index:
        return None
    word_positions = []
    for word, positions in abstract_inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(word for _, word in word_positions)


def normalize_openalex_data(data):
    results = data.get("results", [])
    normalized = []
    for item in results:
        abstract_inverted_index = item.get("abstract_inverted_index")
        if abstract_inverted_index:
            abstract = reconstruct_abstract(abstract_inverted_index)
        else:
            abstract = None

        normalized.append({
            "id": item.get("id"),
            "title": item.get("display_name"),
            "abstract": abstract,
            "publication_year": item.get("publication_year")
        })
    return normalized



def normalize_semantic_data(data):
    papers = data.get("data", [])
    normalized = []
    for paper in papers:
        normalized.append({
            "paperId": paper.get("paperId"),
            "title": paper.get("title"),
            "abstract": paper.get("abstract"),
            "year": paper.get("year"),
            "authors": ", ".join([author.get("name") for author in paper.get("authors", [])])
        })
    return normalized

def store_to_s3(bucket_name, key, data, aws_region="us-east-1"):
    s3 = boto3.client('s3', region_name=aws_region)
    s3.put_object(Bucket=bucket_name, Key=key, Body=data)
    print(f"Stored data to s3://{bucket_name}/{key}")

def upload_dataframe_to_s3(df, bucket_name, key, aws_region="us-east-1"):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    store_to_s3(bucket_name, key, csv_buffer.getvalue(), aws_region)

def generate_key(prefix, query, suffix, use_timestamp=True):
    safe_query = query.lower().replace(" ", "_")
    if use_timestamp:
        timestamp = int(time.time())
        key = f"{prefix}/{safe_query}_{timestamp}_{suffix}"
    else:
        key = f"{prefix}/{safe_query}_{suffix}"
    return key

def main():
    query = "TOPIC_NAME"
    bucket_name = "BUCKET_NAME"
    aws_region = "us-east-1"

    openalex_raw = fetch_openalex_data(query)
    semantic_raw = fetch_semantic_scholar_data(query)

    openalex_raw_key = generate_key("raw", query, "openalex_raw.json")
    semantic_raw_key = generate_key("raw", query, "semantic_raw.json")
    openalex_csv_key = generate_key("normalized", query, "openalex_data.csv")
    semantic_csv_key = generate_key("normalized", query, "semantic_data.csv")

    store_to_s3(bucket_name, openalex_raw_key, json.dumps(openalex_raw, indent=2), aws_region)
    store_to_s3(bucket_name, semantic_raw_key, json.dumps(semantic_raw, indent=2), aws_region)

    openalex_normalized = normalize_openalex_data(openalex_raw)
    semantic_normalized = normalize_semantic_data(semantic_raw)

    df_openalex = pd.DataFrame(openalex_normalized)
    df_semantic = pd.DataFrame(semantic_normalized)

    upload_dataframe_to_s3(df_openalex, bucket_name, openalex_csv_key, aws_region)
    upload_dataframe_to_s3(df_semantic, bucket_name, semantic_csv_key, aws_region)

if __name__ == "__main__":
    main()
