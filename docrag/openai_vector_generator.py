import os
from openai import OpenAI
from typing import List, Dict
import time

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text: str) -> List[float]:
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        if "Rate limit" in str(e):
            print("Rate limit exceeded. Waiting for 20 seconds.")
            time.sleep(20)
            return generate_embedding(text)
        else:
            print(f"An error occurred: {e}")
            return []

def process_chunks(chunks: List[Dict]) -> List[Dict]:
    processed_chunks = []
    for chunk in chunks:
        embedding = generate_embedding(chunk['text'])
        if embedding:
            processed_chunks.append({
                'text': chunk['text'],
                'metadata': chunk['metadata'],
                'vector': embedding
            })
    return processed_chunks

if __name__ == "__main__":
    # Assume chunks is the list of processed chunks from the previous script
    chunks = [...]  # List of chunks from markdown processor
    vectorized_chunks = process_chunks(chunks)
    print(f"Generated embeddings for {len(vectorized_chunks)} chunks.")