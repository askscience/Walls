"""
Sets up the RAG query engine.
"""

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SentenceTransformerRerank

def setup_rag_query_engine(index: VectorStoreIndex, llm):
    """
    Initializes and returns a LlamaIndex QueryEngine.

    Args:
        index (VectorStoreIndex): The VectorStoreIndex to query.
        llm: The Ollama LLM instance.

    Returns:
        RetrieverQueryEngine: The configured query engine.
    """
    Settings.llm = llm
    retriever = VectorIndexRetriever(index=index, similarity_top_k=10) # Retrieve more for re-ranking
    
    # Configure re-ranker
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2", top_n=5 # Number of top documents to pass to LLM after re-ranking
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[reranker]
    )

    # Override the _query method to add debug prints
    original_query_method = query_engine._query

    def custom_query_method(query_bundle):
        print("\n--- Retrieved Nodes (before re-ranking) ---")
        nodes = retriever.retrieve(query_bundle)
        for i, node in enumerate(nodes):
            print(f"Node {i+1} (Score: {node.score:.2f}):\n{node.text[:200]}...") # Print first 200 chars

        print("\n--- Retrieved Nodes (after re-ranking) ---")
        processed_nodes = reranker.postprocess_nodes(nodes, query_bundle)
        for i, node in enumerate(processed_nodes):
            print(f"Node {i+1} (Score: {node.score:.2f}):\n{node.text[:200]}...") # Print first 200 chars

        # Construct the prompt that will be sent to the LLM
        # This is a simplified representation, actual prompt construction is internal to LlamaIndex
        # but this gives an idea of the context passed.
        context_str = "\n\n".join([n.text for n in processed_nodes])
        print("\n--- Context sent to LLM ---")
        print(context_str)
        print("\n--- Query sent to LLM ---")
        print(query_bundle.query_str)

        return original_query_method(query_bundle)

    query_engine._query = custom_query_method
    
    return query_engine
