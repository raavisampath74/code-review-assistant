"""
RAG Pipeline Module
Implements Retrieval-Augmented Generation pipeline for code review.
"""

from typing import Optional, Dict, Any, List

from langchain.chains import RetrievalQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate

from vector_store.chroma_client import ChromaVectorStore
from retriever.retriever import CodeRetriever
from llm.llm_client import get_llm_client, BaseLLMClient
from prompts.code_review_prompt import get_review_prompt, get_system_prompt
from utils.formatter import ReviewReport, parse_llm_response


class RAGPipeline:
    """Implements RAG pipeline for context-aware code review."""
    
    def __init__(
        self,
        vector_store: ChromaVectorStore,
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None,
        top_k: int = 5,
        temperature: float = 0.3
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            vector_store: ChromaDB vector store
            llm_provider: LLM provider (openai, vertex_ai)
            llm_model: LLM model name
            api_key: API key for LLM
            top_k: Number of documents to retrieve
            temperature: LLM temperature
        """
        self.vector_store = vector_store
        self.retriever = CodeRetriever(vector_store, top_k=top_k)
        self.llm_client = get_llm_client(
            provider=llm_provider,
            api_key=api_key,
            model=llm_model,
            temperature=temperature
        )
        self.top_k = top_k
        self.system_prompt = get_system_prompt()
    
    def review_code(
        self,
        code: str,
        review_type: str = "general",
        include_context: bool = True,
        additional_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Perform RAG-based code review.
        
        Args:
            code: Source code to review
            review_type: Type of review (general, security, performance, readability)
            include_context: Whether to include retrieved context
            additional_instructions: Extra instructions for the review
            
        Returns:
            Dictionary with review results
        """
        # Step 1: Retrieve relevant context
        context = ""
        context_metadata = []
        
        if include_context:
            context_result = self.retriever.retrieve_for_review(code, review_type)
            context = context_result["context_text"]
            context_metadata = context_result["source_metadata"]
        
        # Step 2: Generate prompt
        prompt = get_review_prompt(
            code=code,
            context=context,
            review_type=review_type,
            instructions=additional_instructions,
            focus_areas=self._get_focus_areas(review_type)
        )
        
        # Step 3: Generate review using LLM
        response = self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )
        
        # Step 4: Parse and structure the response
        report = parse_llm_response(response)
        
        return {
            "raw_response": response,
            "report": report,
            "context_used": len(context_metadata) > 0,
            "context_sources": context_metadata,
            "review_type": review_type
        }
    
    def _get_focus_areas(self, review_type: str) -> str:
        """Get focus areas based on review type."""
        focus_map = {
            "general": "code quality, readability, and best practices",
            "security": "security vulnerabilities and data protection",
            "performance": "performance optimization and efficiency",
            "readability": "code clarity, naming, and documentation"
        }
        return focus_map.get(review_type, focus_map["general"])
    
    def quick_review(self, code: str) -> str:
        """
        Perform a quick code review without context retrieval.
        
        Args:
            code: Code to review
            
        Returns:
            Quick review response
        """
        from prompts.code_review_prompt import get_quick_review_prompt
        
        prompt = get_quick_review_prompt(code)
        return self.llm_client.generate(prompt)
    
    def multi_review(
        self,
        code: str,
        review_types: List[str] = ["general", "security", "performance"]
    ) -> Dict[str, Any]:
        """
        Perform multiple types of reviews on the same code.
        
        Args:
            code: Code to review
            review_types: List of review types
            
        Returns:
            Combined review results
        """
        results = {}
        all_issues = []
        
        for review_type in review_types:
            result = self.review_code(code, review_type, include_context=True)
            results[review_type] = result
            all_issues.extend(result["report"].issues)
        
        # Create combined summary
        combined_report = ReviewReport(
            issues=all_issues,
            summary=f"Combined review covering: {', '.join(review_types)}",
            overall_score=self._calculate_combined_score(results)
        )
        
        return {
            "individual_reviews": results,
            "combined_report": combined_report
        }
    
    def _calculate_combined_score(self, results: Dict) -> int:
        """Calculate weighted average score."""
        scores = [r["report"].overall_score for r in results.values()]
        return int(sum(scores) / len(scores)) if scores else 5
    
    def add_to_knowledge_base(self, code_chunks: List[Any]) -> List[str]:
        """
        Add code chunks to the knowledge base.
        
        Args:
            code_chunks: List of CodeChunk objects
            
        Returns:
            List of document IDs
        """
        return self.vector_store.add_code_chunks(code_chunks)


def create_rag_pipeline(
    persist_directory: str = "./chroma_db",
    embedding_provider: str = "huggingface",
    llm_provider: str = "openai",
    api_key: Optional[str] = None,
    **kwargs
) -> RAGPipeline:
    """
    Create a RAG pipeline instance.
    
    Args:
        persist_directory: Directory for vector store
        embedding_provider: Embedding provider
        llm_provider: LLM provider
        api_key: API key
        
    Returns:
        RAGPipeline instance
    """
    vector_store = ChromaVectorStore(
        persist_directory=persist_directory,
        embedding_provider=embedding_provider
    )
    
    return RAGPipeline(
        vector_store=vector_store,
        llm_provider=llm_provider,
        api_key=api_key,
        **kwargs
    )
