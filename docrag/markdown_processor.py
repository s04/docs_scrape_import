import re
from pathlib import Path

def clean_markdown(content):
    # Remove code blocks
    content = re.sub(r'```[\s\S]*?```', '', content)
    # Remove inline code
    content = re.sub(r'`[^`\n]+`', '', content)
    # Remove links
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    # Remove special characters
    content = re.sub(r'[#*_~]', '', content)
    return content

def split_into_chunks(content, chunk_size=1000):
    words = content.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for space
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    cleaned_content = clean_markdown(content)
    chunks = split_into_chunks(cleaned_content)
    
    return [
        {
            'text': chunk,
            'metadata': {
                'file_path': str(file_path),
                'chunk_id': i
            }
        }
        for i, chunk in enumerate(chunks)
    ]

def process_all_markdown_files(markdown_files):
    all_chunks = []
    for file_path in markdown_files:
        all_chunks.extend(process_markdown_file(Path(file_path)))
    return all_chunks

if __name__ == "__main__":
    # Assume markdown_files is a list of file paths from the previous script
    markdown_files = [...]  # List of markdown file paths
    processed_chunks = process_all_markdown_files(markdown_files)
    print(f"Processed {len(processed_chunks)} chunks from {len(markdown_files)} files.")