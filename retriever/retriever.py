"""
Retriever Module
Performs similarity search to fetch relevant context for code review.
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document

from vector_store.chroma_client import ChromaVectorStore


class CodeRetriever:
    """Retrieves relevant code context for review."""
    
    def __init__(self, vector_store: ChromaVectorStore, top_k: int = 5):
        """
        Initialize the code retriever.
        
        Args:
            vector_store: ChromaDB vector store instance
            top_k: Number of documents to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k
    
    def retrieve_context(
        self,
        query: str,
        k: Optional[int] = None,
        filter_type: Optional[str] = None
    ) -> List[Document]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Search query (code snippet or review topic)
            k: Number of results (overrides default)
            filter_type: Filter by chunk type (function, class, etc.)
            
        Returns:
            List of relevant documents
        """
        k = k or self.top_k
        filter_dict = {"chunk_type": filter_type} if filter_type else None
        
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter_dict=filter_dict
        )
    
    def retrieve_with_scores(
        self,
        query: str,
        k: Optional[int] = None,
        min_score: float = 0.5
    ) -> List[tuple]:
        """
        Retrieve context with relevance scores.
        
        Args:
            query: Search query
            k: Number of results
            min_score: Minimum relevance score threshold
            
        Returns:
            List of (Document, score) tuples above threshold
        """
        k = k or self.top_k
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Filter by minimum score
        return [(doc, score) for doc, score in results if score >= min_score]
    
    def retrieve_for_review(
        self,
        code_snippet: str,
        review_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Retrieve context specifically for code review.
        
        Args:
            code_snippet: Code to be reviewed
            review_type: Type of review (general, security, performance)
            
        Returns:
            Dictionary with retrieved context and metadata
        """
        # Create enhanced query based on review type
        review_queries = {
            "general": f"Code quality and best practices for: {code_snippet[:200]}",
            "security": f"Security vulnerabilities in: {code_snippet[:200]}",
            "performance": f"Performance issues in: {code_snippet[:200]}",
            "readability": f"Code readability and style: {code_snippet[:200]}"
        }
        
        query = review_queries.get(review_type, review_queries["general"])
        
        # Retrieve relevant documents
        docs = self.retrieve_context(query)
        
        # Organize context
        context = {
            "review_type": review_type,
            "retrieved_docs": len(docs),
            "context_text": self._format_context(docs),
            "source_metadata": [doc.metadata for doc in docs]
        }
        
        return context
    
    def _format_context(self, docs: List[Document]) -> str:
        """Format retrieved documents into context string."""
        if not docs:
            return "No relevant context found in knowledge base."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            context_parts.append(f"""
--- Context #{i} ---
Type: {metadata.get('chunk_type', 'unknown')}
Name: {metadata.get('name', 'unknown')}
Lines: {metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}
Content:
{doc.page_content}
""")
        
        return "\n".join(context_parts)
    
    def get_retriever(self):
        """Get LangChain retriever for chain integration."""
        return self.vector_store.get_retriever({"k": self.top_k})


def create_retriever(
    vector_store: ChromaVectorStore,
    top_k: int = 5
) -> CodeRetriever:
    """
    Create a code retriever instance.
    
    Args:
        vector_store: Vector store instance
        top_k: Number of documents to retrieve
        
    Returns:
        CodeRetriever instance
    """
    return CodeRetriever(vector_store=vector_store, top_k=top_k)
