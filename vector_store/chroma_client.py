"""
ChromaDB Vector Store Module
Initializes and manages the ChromaDB vector database.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from embeddings.embedder import get_langchain_embeddings


class ChromaVectorStore:
    """Manages ChromaDB vector store operations."""
    
    def __init__(
        self,
        collection_name: str = "code_review_knowledge",
        persist_directory: str = "./chroma_db",
        embedding_provider: str = "huggingface",
        embedding_model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
            embedding_provider: Embedding provider (openai, huggingface)
            embedding_model: Model name for embeddings
            api_key: API key for embedding provider
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = get_langchain_embeddings(
            provider=embedding_provider,
            api_key=api_key,
            model=embedding_model
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize LangChain Chroma wrapper
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document
            
        Returns:
            List of document IDs
        """
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            doc_id = ids[i] if ids else f"doc_{i}"
            documents.append(Document(
                page_content=text,
                metadata={**metadata, "doc_id": doc_id}
            ))
        
        return self.vectorstore.add_documents(documents)
    
    def add_code_chunks(self, chunks: List[Any]) -> List[str]:
        """
        Add parsed code chunks to the vector store.
        
        Args:
            chunks: List of CodeChunk objects
            
        Returns:
            List of document IDs
        """
        texts = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk.content)
            metadatas.append({
                "chunk_type": chunk.chunk_type,
                "name": chunk.name,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "docstring": chunk.docstring or ""
            })
            ids.append(f"chunk_{chunk.chunk_type}_{chunk.name}_{i}")
        
        return self.add_documents(texts, metadatas, ids)
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of matching documents
        """
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of (Document, score) tuples
        """
        return self.vectorstore.similarity_search_with_relevance_scores(
            query=query,
            k=k
        )
    
    def get_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        Get a retriever for the vector store.
        
        Args:
            search_kwargs: Search parameters
            
        Returns:
            Retriever object
        """
        kwargs = search_kwargs or {"k": 5}
        return self.vectorstore.as_retriever(search_kwargs=kwargs)
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            # Recreate the collection
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        collection = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "count": collection.count(),
            "persist_directory": self.persist_directory
        }


def create_vector_store(
    collection_name: str = "code_review_knowledge",
    persist_directory: str = "./chroma_db",
    embedding_provider: str = "huggingface"
) -> ChromaVectorStore:
    """
    Create a ChromaDB vector store instance.
    
    Args:
        collection_name: Collection name
        persist_directory: Persistence directory
        embedding_provider: Embedding provider
        
    Returns:
        ChromaVectorStore instance
    """
    return ChromaVectorStore(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_provider=embedding_provider
    )
