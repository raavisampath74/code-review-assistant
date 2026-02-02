"""
LLM Client Module
Connects to OpenAI API or Vertex AI LLMs for code review generation.
"""

import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatVertexAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from the LLM."""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Multi-turn chat with the LLM."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client for code review."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response from OpenAI.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated response text
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = self.llm.invoke(messages)
        return response.content
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Multi-turn chat with OpenAI.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            
        Returns:
            Generated response text
        """
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        response = self.llm.invoke(langchain_messages)
        return response.content


class VertexAIClient(BaseLLMClient):
    """Google Vertex AI client for code review."""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model: str = "gemini-pro",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Initialize Vertex AI client.
        
        Args:
            project_id: GCP project ID
            location: GCP region
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self.model = model
        
        self.llm = ChatVertexAI(
            project=self.project_id,
            location=location,
            model_name=model,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from Vertex AI."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        messages = [HumanMessage(content=full_prompt)]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Multi-turn chat with Vertex AI."""
        langchain_messages = []
        for msg in messages:
            if msg["role"] in ["system", "user"]:
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        response = self.llm.invoke(langchain_messages)
        return response.content


class LLMFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create(
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create an LLM client.
        
        Args:
            provider: LLM provider (openai, vertex_ai)
            api_key: API key
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max tokens
            
        Returns:
            LLM client instance
        """
        if provider.lower() == "openai":
            return OpenAIClient(
                api_key=api_key,
                model=model or "gpt-3.5-turbo",
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif provider.lower() in ["vertex_ai", "vertexai", "google"]:
            return VertexAIClient(
                project_id=kwargs.get("project_id"),
                location=kwargs.get("location", "us-central1"),
                model=model or "gemini-pro",
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")


def get_llm_client(
    provider: str = "openai",
    **kwargs
) -> BaseLLMClient:
    """
    Convenience function to get an LLM client.
    
    Args:
        provider: LLM provider
        **kwargs: Additional arguments for the client
        
    Returns:
        LLM client instance
    """
    return LLMFactory.create(provider=provider, **kwargs)
