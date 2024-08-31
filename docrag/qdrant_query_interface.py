from qdrant_client import QdrantClient
from openai import OpenAI
import os
from typing import List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_query_embedding(query: str) -> List[float]:
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def search_qdrant(client: QdrantClient, collection_name: str, query: str, limit: int = 5):
    query_vector = generate_query_embedding(query)
    
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )
    
    return search_result

def display_results(results):
    for result in results:
        print(f"Score: {result.score}")
        print(f"Text: {result.payload['text']}")
        print(f"File: {result.payload['file_path']}")
        print(f"Chunk ID: {result.payload['chunk_id']}")
        print("---")

if __name__ == "__main__":
    qdrant_client = QdrantClient("localhost", port=6333)
    collection_name = "github_docs"

    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        results = search_qdrant(qdrant_client, collection_name, query)
        display_results(results)