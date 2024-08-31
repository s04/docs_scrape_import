# DocRAG: Documentation Retrieval-Augmented Generation

DocRAG is a Python package that creates a Retrieval-Augmented Generation (RAG) system for Python package documentation. It parses a `requirements.txt` file, finds and processes the documentation for each package, and stores it in a Qdrant vector database for efficient querying.

## Features

- Parse `requirements.txt` files, including custom documentation links
- Automatically find documentation for Python packages (GitHub or ReadTheDocs)
- Process markdown files from documentation
- Generate vector embeddings using OpenAI's API
- Store and query documentation using Qdrant vector database
- Interactive query interface for searching documentation

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/docrag.git
   cd docrag
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Usage

1. Ensure you have a `requirements.txt` file in your project directory.

2. (Optional) Add custom documentation links to your `requirements.txt` file:
   ```
   package_name==1.0.0  # package_name-docrag: "https://github.com/username/repo"
   # another_package-docrag: "https://docs.another_package.com"
   another_package>=2.0.0
   ```

3. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

4. Run DocRAG:
   ```
   docrag
   ```

5. Once the system is ready, you can enter queries to search the documentation.

## Project Structure

- `docrag/`
  - `__init__.py`: Makes the package importable and defines the main entry point.
  - `main.py`: Orchestrates the entire process of parsing requirements, processing docs, and setting up the query interface.
  - `requirements_parser.py`: Parses the `requirements.txt` file, including custom doc links.
  - `doc_finder.py`: Locates documentation for each package (GitHub, ReadTheDocs, or custom URLs).
  - `github_docs_extractor.py`: Clones or updates GitHub repositories and finds markdown files.
  - `markdown_processor.py`: Processes markdown files, cleaning and chunking the content.
  - `openai_vector_generator.py`: Generates vector embeddings for text chunks using OpenAI's API.
  - `qdrant_uploader.py`: Sets up the Qdrant collection and uploads vector data.
  - `qdrant_query_interface.py`: Provides an interface for querying the Qdrant database.

- `setup.py`: Defines the package and its dependencies for installation.

## File Descriptions

1. `main.py`: This is the entry point of the application. It coordinates the entire process, from parsing requirements to setting up the query interface.

2. `requirements_parser.py`: Parses the `requirements.txt` file, extracting package names and versions. It also looks for custom documentation links in comments.

3. `doc_finder.py`: Attempts to find documentation for each package. It handles custom URLs, GitHub repositories, and ReadTheDocs pages.

4. `github_docs_extractor.py`: Manages the cloning or updating of GitHub repositories and identifies markdown files within them.

5. `markdown_processor.py`: Processes markdown files by cleaning the content and splitting it into manageable chunks.

6. `openai_vector_generator.py`: Uses OpenAI's API to generate vector embeddings for the processed text chunks.

7. `qdrant_uploader.py`: Handles the setup of the Qdrant collection and the uploading of vector data to the database.

8. `qdrant_query_interface.py`: Provides functions for querying the Qdrant database and displaying results.

## Customization

You can customize the behavior of DocRAG by modifying the following:

- Change the target Qdrant server in `main.py` by modifying the `QdrantClient` initialization.
- Adjust the chunk size for processing markdown in `markdown_processor.py`.
- Modify the embedding model or parameters in `openai_vector_generator.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.