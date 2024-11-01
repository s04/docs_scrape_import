from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Set
from tqdm import tqdm
import hashlib

def get_file_hash(file_path: str, content: str) -> str:
    """Generate a hash for a file's content"""
    return hashlib.md5(content.encode()).hexdigest()

def get_existing_file_hashes(client: QdrantClient, collection_name: str) -> Dict[str, str]:
    """Retrieve existing file hashes from Qdrant"""
    try:
        # Scroll through all points to get unique file paths and their hashes
        file_hashes = {}
        offset = 0
        limit = 100
        
        while True:
            results = client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(),
                limit=limit,
                offset=offset
            )[0]
            
            if not results:
                break
                
            for point in results:
                file_path = point.payload.get('file_path')
                file_hash = point.payload.get('file_hash')
                if file_path and file_hash:
                    file_hashes[file_path] = file_hash
            
            offset += limit
            
        return file_hashes
    except Exception as e:
        print(f"Error getting existing file hashes: {e}")
        return {}

def setup_qdrant_collection(client: QdrantClient, collection_name: str, vector_size: int):
    """Set up or verify Qdrant collection"""
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(col.name == collection_name for col in collections)
        
        if not exists:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
    except Exception as e:
        print(f"Error setting up collection: {e}")
        # Recreate collection if there's an error
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

def delete_file_points(client: QdrantClient, collection_name: str, file_path: str):
    """Delete all points for a specific file"""
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="file_path",
                        match=MatchValue(value=file_path)
                    )
                ]
            )
        )
    except Exception as e:
        print(f"Error deleting points for file {file_path}: {e}")

def upload_to_qdrant(client: QdrantClient, collection_name: str, chunks: List[Dict], batch_size: int = 100):
    """Upload chunks to Qdrant with file versioning"""
    if not chunks:
        print("No chunks to upload")
        return

    total_chunks = len(chunks)
    processed_files = set()
    
    # Get existing file hashes
    existing_hashes = get_existing_file_hashes(client, collection_name)
    
    with tqdm(total=total_chunks, desc="Uploading to Qdrant") as pbar:
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            current_batch_points = []
            
            for idx, chunk in enumerate(batch):
                file_path = chunk['metadata']['file_path']
                
                # Only process each file once
                if file_path in processed_files:
                    continue
                
                # Calculate hash for the current file content
                file_content = '\n'.join(c['text'] for c in chunks if c['metadata']['file_path'] == file_path)
                current_hash = get_file_hash(file_path, file_content)
                
                # Skip if file hasn't changed
                if file_path in existing_hashes and existing_hashes[file_path] == current_hash:
                    processed_files.add(file_path)
                    continue
                
                # If file has changed or is new, delete old points and add new ones
                if file_path not in processed_files:
                    delete_file_points(client, collection_name, file_path)
                    processed_files.add(file_path)
                
                current_batch_points.append(
                    PointStruct(
                        id=idx + i,
                        vector=chunk['vector'],
                        payload={
                            'text': chunk['text'],
                            'file_path': file_path,
                            'chunk_id': chunk['metadata']['chunk_id'],
                            'file_hash': current_hash
                        }
                    )
                )
            
            if current_batch_points:
                try:
                    client.upsert(
                        collection_name=collection_name,
                        points=current_batch_points,
                        wait=True
                    )
                except Exception as e:
                    print(f"Error uploading batch {i//batch_size + 1}: {str(e)}")
                    if batch_size > 10:
                        print("Retrying with smaller batch size...")
                        return upload_to_qdrant(client, collection_name, chunks, batch_size=batch_size//2)
                    else:
                        raise e
            
            pbar.update(len(batch))
    
    print(f"\nProcessed {len(processed_files)} files:")
    print(f"- Skipped: {len([f for f in processed_files if f in existing_hashes and existing_hashes[f] == get_file_hash(f, ''.join(c['text'] for c in chunks if c['metadata']['file_path'] == f))])}")
    print(f"- Updated/New: {len([f for f in processed_files if f not in existing_hashes or existing_hashes[f] != get_file_hash(f, ''.join(c['text'] for c in chunks if c['metadata']['file_path'] == f))])}")

if __name__ == "__main__":
    # Assume vectorized_chunks is the list from the previous script
    vectorized_chunks = [...]  # List of chunks with embeddings

    client = QdrantClient("localhost", port=6333)
    collection_name = "github_docs"
    vector_size = len(vectorized_chunks[0]['vector'])

    setup_qdrant_collection(client, collection_name, vector_size)
    upload_to_qdrant(client, collection_name, vectorized_chunks)
    print(f"Uploaded {len(vectorized_chunks)} chunks to Qdrant collection '{collection_name}'")