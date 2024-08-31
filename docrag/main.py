import os
from openai import OpenAI
from qdrant_client import QdrantClient

from requirements_parser import parse_requirements
from doc_finder import process_package_docs
from markdown_processor import process_all_markdown_files
from openai_vector_generator import process_chunks
from qdrant_uploader import setup_qdrant_collection, upload_to_qdrant
from qdrant_query_interface import search_qdrant, display_results

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main(requirements_file):
    # Step 1: Parse requirements file
    packages = parse_requirements(requirements_file)
    print(f"Found {len(packages)} packages in requirements file.")

    # Step 2: Process documentation for each package
    all_markdown_files = []
    for package_info in packages:
        print(f"Processing documentation for {package_info['name']}...")
        target_dir = f"docs_{package_info['name']}"
        markdown_files = process_package_docs(package_info, target_dir)
        all_markdown_files.extend(markdown_files)

    print(f"Found {len(all_markdown_files)} markdown files in total.")

    # Step 3: Process markdown files
    print("Processing markdown files...")
    processed_chunks = process_all_markdown_files(all_markdown_files)
    print(f"Processed {len(processed_chunks)} chunks.")

    # Step 4: Generate vector embeddings
    print("Generating vector embeddings...")
    vectorized_chunks = process_chunks(processed_chunks)
    print(f"Generated embeddings for {len(vectorized_chunks)} chunks.")

    # Step 5: Set up Qdrant and upload vectors
    print("Setting up Qdrant and uploading vectors...")
    qdrant_client = QdrantClient("localhost", port=6333)
    collection_name = "package_docs"
    vector_size = len(vectorized_chunks[0]['vector'])
    setup_qdrant_collection(qdrant_client, collection_name, vector_size)
    upload_to_qdrant(qdrant_client, collection_name, vectorized_chunks)
    print(f"Uploaded {len(vectorized_chunks)} chunks to Qdrant collection '{collection_name}'")

    # Step 6: Query interface
    print("\nRAG system is ready. You can now query the documentation.")
    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        results = search_qdrant(qdrant_client, collection_name, query)
        display_results(results)

if __name__ == "__main__":
    requirements_file = "requirements.txt"
    main(requirements_file)