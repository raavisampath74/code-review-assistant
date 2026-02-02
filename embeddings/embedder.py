"""
Embedding Generator Module
Generates vector embeddings using OpenAI or Vertex AI models.
"""

import os
from typing import List, Optional
from abc import ABC, abstractmethod

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


class BaseEmbedder(ABC):
    """Abstract base class for embedding generators."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI-based embedding generator."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embedder.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Embedding model name
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.api_key,
            model=self.model
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return self.embeddings.embed_documents(texts)


class HuggingFaceEmbedder(BaseEmbedder):
    """HuggingFace-based embedding generator (local, free)."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize HuggingFace embedder.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return self.embeddings.embed_documents(texts)


class EmbeddingFactory:
    """Factory class for creating embedders."""
    
    @staticmethod
    def create_embedder(
        provider: str = "huggingface",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseEmbedder:
        """
        Create an embedder based on provider.
        
        Args:
            provider: Embedding provider (openai, huggingface)
            api_key: API key for the provider
            model: Model name
            
        Returns:
            Embedder instance
        """
        if provider.lower() == "openai":
            return OpenAIEmbedder(
                api_key=api_key,
                model=model or "text-embedding-ada-002"
            )
        elif provider.lower() == "huggingface":
            return HuggingFaceEmbedder(
                model_name=model or "all-MiniLM-L6-v2"
            )
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")


def get_langchain_embeddings(
    provider: str = "huggingface",
    api_key: Optional[str] = None,
    model: Optional[str] = None
):
    """
    Get LangChain-compatible embeddings object.
    
    Args:
        provider: Embedding provider
        api_key: API key
        model: Model name
        
    Returns:
        LangChain embeddings object
    """
    if provider.lower() == "openai":
        return OpenAIEmbeddings(
            openai_api_key=api_key or os.getenv("OPENAI_API_KEY"),
            model=model or "text-embedding-ada-002"
        )
    elif provider.lower() == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=model or "all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
