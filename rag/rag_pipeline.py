"""Fast version of RAG pipeline setup with lazy imports.

This module provides the same functionality as rag_pipeline.py
but with lazy loading to improve startup performance.
"""

import os

from lazy_imports import (
    VectorStoreIndex, Settings, RetrieverQueryEngine, 
    VectorIndexRetriever, SentenceTransformerRerank
)


def setup_rag_query_engine(index: 'VectorStoreIndex', llm):
    """
    Initializes and returns a LlamaIndex QueryEngine with lazy imports.

    Args:
        index (VectorStoreIndex): The VectorStoreIndex to query.
        llm: The Ollama LLM instance.

    Returns:
        RetrieverQueryEngine: The configured query engine.
    """
    # Ensure Settings are configured
    Settings.llm = llm
    
    retriever = VectorIndexRetriever(index=index, similarity_top_k=10)  # Retrieve more for re-ranking
    
    # Configure re-ranker
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2", top_n=5  # Number of top documents to pass to LLM after re-ranking
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[reranker],
        llm=llm,  # Explicitly pass the LLM
        streaming=True  # Enable streaming responses
    )

    # Override the _query method to add comprehensive debug prints
    original_query_method = query_engine._query

    def debug_query(query_bundle):
        if os.getenv("RAG_DEBUG") == "1":
            print(f"\n{'-'*60}")
            print(f"🔍 RAG DATABASE QUERY")
            print(f"{'-'*60}")
            print(f"📝 User Query: {query_bundle.query_str}")
            print(f"🔍 Searching knowledge base...")
            
        result = original_query_method(query_bundle)
        
        try:
            if os.getenv("RAG_DEBUG") == "1":
                # Try to get source nodes for database information
                if hasattr(result, 'source_nodes') and result.source_nodes:
                    print(f"📚 Found {len(result.source_nodes)} relevant documents:")
                    for i, node in enumerate(result.source_nodes[:3], 1):  # Show top 3
                        if hasattr(node, 'metadata') and node.metadata:
                            file_name = node.metadata.get('file_name', 'Unknown')
                            print(f"   {i}. 📄 {file_name}")
                            if 'file_path' in node.metadata:
                                print(f"      📁 {node.metadata['file_path']}")
                        if hasattr(node, 'text') and node.text:
                            preview = node.text[:100].replace('\n', ' ')
                            print(f"      📖 Preview: {preview}...")
                        print()
                else:
                    print(f"📚 No specific source documents found")
                    
            if hasattr(result, "response"):
                if os.getenv("RAG_DEBUG") == "1":
                    print(f"🤖 AI Response Generated: {len(result.response)} characters")
                    print(f"📤 Response Preview: {result.response[:150].replace(chr(10), ' ')}...")
                    print(f"{'-'*60}\n")
            elif hasattr(result, "response_gen") or hasattr(result, "get_response"):
                # Streaming response: avoid consuming the generator here
                if os.getenv("RAG_DEBUG") == "1":
                    print(f"🤖 AI Streaming Response Started")
                    print(f"{'-'*60}\n")
            else:
                if os.getenv("RAG_DEBUG") == "1":
                    print(f"🤖 Response Type: {type(result)}")
                    print(f"{'-'*60}\n")
        except Exception as e:
            if os.getenv("RAG_DEBUG") == "1":
                print(f"⚠️  RAG Debug Error: {e}")
                print(f"{'-'*60}\n")
        return result

    query_engine._query = debug_query

    return query_engine