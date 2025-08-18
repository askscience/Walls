"""
Sets up the Ollama LLM and embedding models.
"""

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

def setup_ollama_models(llm_model: str, embedding_model: str, request_timeout: float):
    """
    Initializes and returns instances of Ollama (for LLM) and OllamaEmbedding.

    Args:
        llm_model (str): The name of the Ollama LLM to use.
        embedding_model (str): The name of the Ollama embedding model to use.
        request_timeout (float): The timeout for Ollama API requests.

    Returns:
        tuple: A tuple containing the Ollama LLM instance and the OllamaEmbedding instance.
    """
    system_prompt = (
        "You are an expert assistant. Use the following pieces of context to answer the user's question. "
        "Answer based solely on the context provided. "
        "If the information is not in the context, just say 'I do not have enough information to answer'."
    )
    
    llm = Ollama(
        model=llm_model, 
        request_timeout=request_timeout,
        system_prompt=system_prompt  # Add the system prompt here
    )
    embedding_model = OllamaEmbedding(model_name=embedding_model)
    return llm, embedding_model
