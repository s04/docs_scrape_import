import os
import asyncio
from openai import OpenAI
from qdrant_client import QdrantClient

# Import functions from our previous scripts
from github_docs_extractor import clone_or_pull_repo, find_markdown_files
from markdown_processor import process_all_markdown_files
from openai_vector_generator import process_chunks
from qdrant_uploader import setup_qdrant_collection, upload_to_qdrant
from qdrant_query_interface import search_qdrant, display_results

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

    # Step 3: Generate vector embeddings
    print("Generating vector embeddings...")
    vectorized_chunks = await process_chunks(processed_chunks)
    print(f"Generated embeddings for {len(vectorized_chunks)} chunks.")

    # Step 4: Set up Qdrant and upload vectors
    print("Setting up Qdrant and uploading vectors...")
    qdrant_client = QdrantClient("localhost", port=6333)
    collection_name = "github_docs"
    vector_size = len(vectorized_chunks[0]["vector"])
    setup_qdrant_collection(qdrant_client, collection_name, vector_size)
    upload_to_qdrant(qdrant_client, collection_name, vectorized_chunks)
    print(
        f"Uploaded {len(vectorized_chunks)} chunks to Qdrant collection '{collection_name}'"
    )

    # Step 5: Query interface
    print("\nRAG system is ready. You can now query the documentation.")
    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query.lower() == "quit":
            break

        results = search_qdrant(qdrant_client, collection_name, query)
        display_results(results)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
