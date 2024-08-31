# RAG System for GitHub Documentation

This project implements a Retrieval-Augmented Generation (RAG) system for GitHub documentation. It clones a specified GitHub repository, processes its markdown files, generates vector embeddings, and stores them in a Qdrant vector database. Users can then query the system to retrieve relevant documentation snippets.

## Components

1. **GitHub Docs Extractor**: Clones the repository and identifies markdown files.
2. **Markdown Processor**: Cleans and chunks the markdown content.
3. **OpenAI Vector Generator**: Generates vector embeddings for text chunks using OpenAI's API.
4. **Qdrant Uploader**: Sets up a Qdrant collection and uploads vector data.
5. **Qdrant Query Interface**: Provides a simple interface to search the documentation.
6. **Main Script**: Orchestrates the entire workflow.

## Prerequisites

- Python 3.7+
- Docker (for running Qdrant)
- OpenAI API key

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/your-username/rag-github-docs.git
   cd rag-github-docs
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Start Qdrant using Docker:
   ```
   docker run -p 6333:6333 -p 6334:6334 \
       -v $(pwd)/qdrant_storage:/qdrant/storage:z \
       qdrant/qdrant
   ```

4. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the main script:
   ```
   python rag_github_docs_main.py
   ```

2. The script will:
   - Clone the specified GitHub repository
   - Process all markdown files
   - Generate vector embeddings
   - Upload the vectors to Qdrant
   - Start an interactive query interface

3. Once the setup is complete, you can enter queries to search the documentation.

4. Type 'quit' to exit the query interface.

## Customization

To use this system with a different GitHub repository:

1. Open `rag_github_docs_main.py`
2. Modify the `repo_url` variable to point to your desired repository
3. Run the script as described in the Usage section

## Updating the RAG Database

To update the RAG database with new content:

1. Delete the cloned repository directory (`docs-gitbook`)
2. Re-run the main script

This will re-clone the repository, process any new or updated files, and update the Qdrant collection.

## Note on API Usage

This system uses OpenAI's API to generate vector embeddings. Be mindful of your API usage to avoid unexpected costs.

## Contributing

Contributions to improve the system are welcome. Please feel free to submit issues or pull requests.

## License

[MIT License](LICENSE)