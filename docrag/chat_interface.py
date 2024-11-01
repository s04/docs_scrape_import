from typing import List, Dict, Optional
from dataclasses import dataclass
from openai import OpenAI
import os
from qdrant_query_interface import search_qdrant
from qdrant_client import QdrantClient

@dataclass
class Message:
    role: str  # "system", "user", or "assistant"
    content: str

@dataclass
class Document:
    title: str
    contents: str

class ChatInterface:
    def __init__(self, qdrant_client: QdrantClient, collection_name: str):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.conversation_history: List[Message] = []
        self.context_documents: List[Document] = []
        
        # Initialize with system message
        self.conversation_history.append(Message(
            role="system",
            content="You are a helpful assistant with access to documentation. Use the provided documentation context to give accurate answers. If you're not sure about something, say so."
        ))

    def _get_relevant_docs(self, query: str) -> List[Document]:
        """Search for relevant documents based on the query"""
        results = search_qdrant(
            self.qdrant_client, 
            self.collection_name, 
            query,
            limit=3
        )
        
        docs = []
        for result in results:
            doc = Document(
                title=result.payload['file_path'],
                contents=result.payload['text']
            )
            # Only add if not already in context
            if not any(d.title == doc.title and d.contents == doc.contents 
                      for d in self.context_documents):
                docs.append(doc)
        
        return docs

    def _format_context(self, docs: List[Document]) -> str:
        """Format documents into a string context"""
        context = []
        for doc in docs:
            context.append(f"<title>{doc.title}</title>")
            context.append(f"<contents>{doc.contents}</contents>")
        return "\n\n".join(context)

    def chat(self, user_input: str) -> str:
        """Process user input and return assistant's response"""
        # Get relevant documents
        new_docs = self._get_relevant_docs(user_input)
        self.context_documents.extend(new_docs)
        
        # Print the files being used for context
        print("\nRelevant documentation files:")
        for doc in new_docs:
            print(f"- {doc.title}")
        
        # Format context from all documents
        context = self._format_context(self.context_documents)
        
        # Add user message with context
        user_message = (
            f"Context:\n{context}\n\n"
            f"User Question: {user_input}"
        )
        self.conversation_history.append(Message(role="user", content=user_message))
        
        # Create messages for API
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
        
        # Get completion from OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant's response to history
            self.conversation_history.append(
                Message(role="assistant", content=assistant_response)
            )
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error getting response from OpenAI: {str(e)}"
            print(error_msg)
            return error_msg