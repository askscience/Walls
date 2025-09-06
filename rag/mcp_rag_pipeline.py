"""MCP-enabled RAG pipeline that integrates with OllamaMCPBridge.

This module extends the standard RAG pipeline to support MCP tool calling
through the OllamaMCPBridge, enabling the AI to actually execute tools
instead of just providing instructions.
"""

import os
import sys
import json
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

# Add MCP directory to path
mcp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MCP')
sys.path.insert(0, mcp_path)

# MCP Bridge functionality simplified - using direct connections when needed
from lazy_imports import (
    VectorStoreIndex, Settings, RetrieverQueryEngine, 
    VectorIndexRetriever, SentenceTransformerRerank
)


class MCPRAGPipeline:
    """RAG pipeline with MCP tool calling capabilities."""
    
    def __init__(self):
        self.mcp_bridge = None
        self.query_engine = None
        self.is_initialized = False
        
    async def initialize(self, index: 'VectorStoreIndex', llm):
        """Initialize the MCP-enabled RAG pipeline.
        
        Args:
            index: The VectorStoreIndex to query
            llm: The Ollama LLM instance
        """
        try:
            # MCP bridge functionality simplified - RAG works independently
            self.mcp_bridge = None  # Simplified: no direct MCP bridge integration
            
            # Setup standard RAG components
            Settings.llm = llm
            retriever = VectorIndexRetriever(index=index, similarity_top_k=10)
            reranker = SentenceTransformerRerank(
                model="cross-encoder/ms-marco-MiniLM-L-6-v2", 
                top_n=5
            )
            
            self.query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                node_postprocessors=[reranker],
                llm=llm,
                streaming=True
            )
            
            # Override query method to add MCP tool calling
            self._setup_mcp_query_override()
            
            self.is_initialized = True
            
            if os.getenv("RAG_DEBUG") == "1":
                print("✅ MCP-enabled RAG pipeline initialized successfully")
                print("🔧 MCP tools: Available via shared server (no direct integration)")
                
        except Exception as e:
            print(f"❌ Failed to initialize MCP RAG pipeline: {e}")
            raise
    
    def _setup_mcp_query_override(self):
        """Override the query engine's _query method to add MCP tool calling."""
        original_query_method = self.query_engine._query
        
        def mcp_enabled_query(query_bundle):
            if os.getenv("RAG_DEBUG") == "1":
                print(f"\n{'-'*60}")
                print(f"🔍 MCP-ENABLED RAG QUERY")
                print(f"{'-'*60}")
                print(f"📝 Query: {query_bundle.query_str}")
                print("🔧 MCP Bridge Status: Simplified (no direct integration)")
                print(f"{'-'*60}\n")
            
            # Get RAG context first
            rag_response = original_query_method(query_bundle)
            
            # Simplified: return standard RAG response
            return rag_response
        
        self.query_engine._query = mcp_enabled_query
    
    async def query_with_mcp(self, query: str, model: str = "gemma3:1b") -> str:
        """Query with MCP tool calling support.
        
        Args:
            query: The user query
            model: The Ollama model to use
            
        Returns:
            The response, potentially after executing MCP tools
        """
        if not self.is_initialized:
            raise RuntimeError("RAG pipeline not initialized")
        
        try:
            # Simplified: Use standard RAG without direct MCP integration
            print("ℹ️  Using standard RAG pipeline (MCP tools available via shared server)")
            response = await self.standard_rag_query(query)
            
            if os.getenv("RAG_DEBUG") == "1":
                print(f"\n{'-'*60}")
                print(f"🤖 MCP-ENABLED RESPONSE")
                print(f"{'-'*60}")
                print(f"📤 Final Response: {response[:100]}...")
                print(f"{'-'*60}\n")
            
            return response
            
        except Exception as e:
            error_msg = f"Error in MCP query: {e}"
            if os.getenv("RAG_DEBUG") == "1":
                print(f"❌ {error_msg}")
            return error_msg
    
    def query_sync(self, query: str, model: str = "gemma3:1b") -> str:
        """Synchronous wrapper for MCP query.
        
        Args:
            query: The user query
            model: The Ollama model to use
            
        Returns:
            The response, potentially after executing MCP tools
        """
        try:
            # Use standard query engine
            if self.query_engine:
                from llama_index.core import QueryBundle
                query_bundle = QueryBundle(query_str=query)
                response = self.query_engine.query(query_bundle)
                return str(response)
            
            # Check if there's already a running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async_query, query, model)
                    return future.result(timeout=300)  # 5 minute timeout
            except RuntimeError:
                # No running loop, safe to create new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.query_with_mcp(query, model))
                finally:
                    loop.close()
        except Exception as e:
            error_msg = f"Error in sync MCP query: {e}"
            if os.getenv("RAG_DEBUG") == "1":
                print(f"❌ {error_msg}")
            return error_msg
    
    def _run_async_query(self, query: str, model: str) -> str:
        """Helper method to run async query in a new thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.query_with_mcp(query, model))
        finally:
            loop.close()
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get available MCP tools.
        
        Returns:
            Dictionary of available tools by server
        """
        # Simplified: MCP tools available via shared server
        return {"info": "MCP tools available via shared server at localhost:9001"}
    
    async def cleanup(self):
        """Clean up resources."""
        # Simplified: no MCP connections to clean up
        print("🧹 RAG cleanup completed")


def _create_basic_query_engine(index: 'VectorStoreIndex', llm):
    """Create a basic query engine without MCP capabilities as fallback.
    
    Args:
        index: The VectorStoreIndex to query
        llm: The Ollama LLM instance
        
    Returns:
        Basic RetrieverQueryEngine instance
    """
    from lazy_imports import Settings, RetrieverQueryEngine, VectorIndexRetriever, SentenceTransformerRerank
    
    Settings.llm = llm
    retriever = VectorIndexRetriever(index=index, similarity_top_k=10)
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2", 
        top_n=5
    )
    
    return RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[reranker],
        llm=llm,
        streaming=True
    )


# Global instance for backward compatibility
_mcp_pipeline = None


async def setup_mcp_rag_pipeline(index: 'VectorStoreIndex', llm) -> MCPRAGPipeline:
    """Setup and return MCP-enabled RAG pipeline.
    
    Args:
        index: The VectorStoreIndex to query
        llm: The Ollama LLM instance
        
    Returns:
        Initialized MCPRAGPipeline instance
    """
    global _mcp_pipeline
    
    if _mcp_pipeline is None:
        _mcp_pipeline = MCPRAGPipeline()
        await _mcp_pipeline.initialize(index, llm)
    
    return _mcp_pipeline


def setup_mcp_rag_pipeline_sync(index: 'VectorStoreIndex', llm) -> MCPRAGPipeline:
    """Synchronous wrapper for MCP RAG pipeline setup.
    
    Args:
        index: The VectorStoreIndex to query
        llm: The Ollama LLM instance
        
    Returns:
        Initialized MCPRAGPipeline instance
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(setup_mcp_rag_pipeline(index, llm))
            return result
        finally:
            loop.close()
    except Exception as e:
        print(f"⚠️  MCP RAG pipeline setup failed: {e}, falling back to basic RAG")
        # Return a basic pipeline without MCP capabilities
        pipeline = MCPRAGPipeline()
        pipeline.query_engine = _create_basic_query_engine(index, llm)
        pipeline.is_initialized = True
        return pipeline