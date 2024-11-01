import os
import asyncio
from openai import AsyncOpenAI
from typing import List, Dict
import time
from tqdm import tqdm

# Initialize the OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_embedding(text: str) -> List[float]:
    try:
        response = await client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        if "Rate limit" in str(e):
            print("Rate limit exceeded. Waiting for 20 seconds.")
            await asyncio.sleep(20)
            return await generate_embedding(text)
        else:
            print(f"An error occurred: {e}")
            return []

async def process_single_chunk(chunk: Dict) -> Dict:
    embedding = await generate_embedding(chunk['text'])
    if embedding:
        return {
            'text': chunk['text'],
            'metadata': chunk['metadata'],
            'vector': embedding
        }
    return None

async def process_chunks(chunks: List[Dict]) -> List[Dict]:
    # Process chunks in batches of 100 for better performance
    batch_size = 100
    processed_chunks = []
    
    with tqdm(total=len(chunks), desc="Generating embeddings") as pbar:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            # Create tasks for the batch
            tasks = [process_single_chunk(chunk) for chunk in batch]
            # Process batch concurrently
            results = await asyncio.gather(*tasks)
            # Filter out None results and add to processed chunks
            processed_chunks.extend([r for r in results if r is not None])
            pbar.update(len(batch))
    
    return processed_chunks