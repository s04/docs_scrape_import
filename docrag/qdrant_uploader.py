from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict

def setup_qdrant_collection(client: QdrantClient, collection_name: str, vector_size: int):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

def upload_to_qdrant(client: QdrantClient, collection_name: str, chunks: List[Dict]):
    points = [
        PointStruct(
            id=i,
            vector=chunk['vector'],
            payload={
                'text': chunk['text'],
                'file_path': chunk['metadata']['file_path'],
                'chunk_id': chunk['metadata']['chunk_id']
            }
        )
        for i, chunk in enumerate(chunks)
    ]

    client.upsert(
        collection_name=collection_name,
        points=points
    )

if __name__ == "__main__":
    # Assume vectorized_chunks is the list from the previous script
    vectorized_chunks = [...]  # List of chunks with embeddings

    client = QdrantClient("localhost", port=6333)
    collection_name = "github_docs"
    vector_size = len(vectorized_chunks[0]['vector'])

    setup_qdrant_collection(client, collection_name, vector_size)
    upload_to_qdrant(client, collection_name, vectorized_chunks)
    print(f"Uploaded {len(vectorized_chunks)} chunks to Qdrant collection '{collection_name}'")