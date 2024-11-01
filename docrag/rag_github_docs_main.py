import os
import asyncio
from openai import OpenAI
from qdrant_client import QdrantClient

# Import functions from our previous scripts
from github_docs_extractor import clone_or_pull_repo, find_markdown_files
from markdown_processor import process_all_markdown_files
from openai_vector_generator import process_chunks
from qdrant_uploader import setup_qdrant_collection, upload_to_qdrant, get_file_hash, get_existing_file_hashes
from qdrant_query_interface import search_qdrant, display_results
from chat_interface import ChatInterface

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def async_main():
    # Step 1: Clone or update repository and find markdown files
    repo_url = "https://github.com/microsoft/playwright"
    target_dir = "docs/src"
    print("Cloning or updating repository and finding markdown files...")
    clone_or_pull_repo(repo_url, target_dir)
    markdown_files = find_markdown_files(target_dir)
    print(f"Found {len(markdown_files)} markdown files.")

    # Step 2: Process markdown files
    print("Processing markdown files...")
    processed_chunks = process_all_markdown_files(markdown_files)
    print(f"Processed {len(processed_chunks)} chunks.")

    # Step 3 & 4: Set up Qdrant first to check existing files
    print("Setting up Qdrant...")
    qdrant_client = QdrantClient("localhost", port=6333)
    collection_name = "github_docs"
    
    # Get existing files from Qdrant
    existing_hashes = get_existing_file_hashes(qdrant_client, collection_name)
    
    # Filter out chunks from unchanged files
    files_to_process = set()
    chunks_to_process = []
    
    for chunk in processed_chunks:
        file_path = chunk['metadata']['file_path']
        if file_path not in files_to_process:
            file_content = '\n'.join(c['text'] for c in processed_chunks if c['metadata']['file_path'] == file_path)
            current_hash = get_file_hash(file_path, file_content)
            
            if file_path not in existing_hashes or existing_hashes[file_path] != current_hash:
                files_to_process.add(file_path)
    
    chunks_to_process = [chunk for chunk in processed_chunks if chunk['metadata']['file_path'] in files_to_process]
    
    if chunks_to_process:
        print(f"Generating embeddings for {len(chunks_to_process)} chunks from {len(files_to_process)} modified/new files...")
        vectorized_chunks = await process_chunks(chunks_to_process)
        
        # Initialize collection if it doesn't exist
        if not existing_hashes:
            vector_size = len(vectorized_chunks[0]["vector"])
            setup_qdrant_collection(qdrant_client, collection_name, vector_size)
        
        # Upload new/modified vectors
        upload_to_qdrant(qdrant_client, collection_name, vectorized_chunks)
    else:
        print("No new or modified files to process.")

    # Step 5: Chat interface
    print("\nRAG system is ready. You can now chat with the documentation.")
    chat_interface = ChatInterface(qdrant_client, collection_name)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break
            
        response = chat_interface.chat(user_input)
        print("\nAssistant:", response)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
