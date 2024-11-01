from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
from tqdm import tqdm

def setup_qdrant_collection(client: QdrantClient, collection_name: str, vector_size: int):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

def upload_to_qdrant(client: QdrantClient, collection_name: str, chunks: List[Dict], batch_size: int = 100):
    total_chunks = len(chunks)
    
    with tqdm(total=total_chunks, desc="Uploading to Qdrant") as pbar:
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            points = [
                PointStruct(
                    id=idx + i,  # Ensure unique IDs across batches
                    vector=chunk['vector'],
                    payload={
                        'text': chunk['text'],
                        'file_path': chunk['metadata']['file_path'],
                        'chunk_id': chunk['metadata']['chunk_id']
                    }
                )
                for idx, chunk in enumerate(batch)
            ]

            try:
                client.upsert(
                    collection_name=collection_name,
                    points=points,
                    wait=True
                )
                pbar.update(len(batch))
            except Exception as e:
                print(f"Error uploading batch {i//batch_size + 1}: {str(e)}")
                # Retry with smaller batch
                if batch_size > 10:
                    print("Retrying with smaller batch size...")
                    return upload_to_qdrant(client, collection_name, chunks, batch_size=batch_size//2)
                else:
                    raise e

if __name__ == "__main__":
    # Assume vectorized_chunks is the list from the previous script
    vectorized_chunks = [...]  # List of chunks with embeddings

    client = QdrantClient("localhost", port=6333)
    collection_name = "github_docs"
    vector_size = len(vectorized_chunks[0]['vector'])

    setup_qdrant_collection(client, collection_name, vector_size)
    upload_to_qdrant(client, collection_name, vectorized_chunks)
    print(f"Uploaded {len(vectorized_chunks)} chunks to Qdrant collection '{collection_name}'")