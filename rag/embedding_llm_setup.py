"""Fast version of embedding LLM setup with lazy imports.

This module provides the same functionality as embedding_llm_setup.py
but with lazy loading to improve startup performance.
"""

from typing import Dict, Any
from lazy_imports import Ollama, OllamaEmbedding
from mcp_rag_pipeline import setup_mcp_rag_pipeline_sync, MCPRAGPipeline
import json
import os


def _load_prompt_from_json() -> str:
    """Load the complete system prompt from prompts.json.
    Falls back to a safe default if the file is missing or malformed.
    """
    prompts_path = os.path.join(os.path.dirname(__file__), "prompts.json")
    try:
        with open(prompts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        default = data.get("system_prompts", {}).get("default", {})
        
        # Get all prompt components from prompts.json
        base_prompt = default.get("base_prompt", "")
        requirements = default.get("command_requirements", "")
        # Combine only normal conversation parts from prompts.json
        prompt_parts = [base_prompt, requirements]
        return " ".join(filter(None, prompt_parts))
    except Exception:
        # Fallback to a minimal prompt
        return "You are a helpful local assistant. Answer concisely using only the retrieved context."


def setup_ollama_models(
    llm_model: str,
    embedding_model: str,
    request_timeout: float,
    model_params: Dict[str, Any],
):
    """
    Initializes and returns instances of Ollama (for LLM) and OllamaEmbedding.
    Uses lazy imports to reduce initial load time.

    Args:
        llm_model (str): The name of the Ollama LLM to use.
        embedding_model (str): The name of the Ollama embedding model to use.
        request_timeout (float): The timeout for Ollama API requests.
        model_params (Dict[str, Any]): Additional parameters for the Ollama model.

    Returns:
        tuple: A tuple containing the Ollama LLM instance and the OllamaEmbedding instance.
    """
    system_prompt = _load_prompt_from_json()

    llm = Ollama(
        model=llm_model,
        request_timeout=request_timeout,
        system_prompt=system_prompt,
        **model_params,
    )
    embedding_model_instance = OllamaEmbedding(model_name=embedding_model)
    
    # Removed blocking preload test call to avoid startup hangs
    
    return llm, embedding_model_instance


def setup_mcp_enabled_rag(
    index,
    llm_model: str = "gemma3:1b",
    embedding_model: str = "nomic-embed-text",
    request_timeout: float = 120.0,
    model_params: Dict[str, Any] = None,
):
    """
    Setup MCP-enabled RAG pipeline with tool calling capabilities.
    
    Args:
        index: The VectorStoreIndex to query
        llm_model (str): The name of the Ollama LLM to use.
        embedding_model (str): The name of the Ollama embedding model to use.
        request_timeout (float): The timeout for Ollama API requests.
        model_params (Dict[str, Any]): Additional parameters for the Ollama model.
    
    Returns:
        MCPRAGPipeline: Initialized MCP-enabled RAG pipeline
    """
    if model_params is None:
        model_params = {}
    
    # Setup standard Ollama models
    llm, embed_model = setup_ollama_models(llm_model, embedding_model, request_timeout, model_params)
    
    # Initialize MCP-enabled RAG pipeline
    mcp_pipeline = setup_mcp_rag_pipeline_sync(index, llm)
    
    return mcp_pipeline