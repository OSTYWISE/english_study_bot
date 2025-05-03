import logging
from app.rag.rag_utils import RAGManager


async def initialize_rag():
    """
    Initialize the RAG system by indexing all literary works.
    """
    logging.info("Initializing RAG system...")
    rag_manager = RAGManager()
    await rag_manager.index_literary_works()
    logging.info("RAG system initialized successfully!")
