import os
import json
from typing import List, Dict, Any, Optional
from app.rag.vector_store import VectorStore
from app.database.requests import get_litwork_by_id


class RAGManager:
    """
    A manager class to handle RAG operations for literary works.
    """
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the RAG manager.
        
        Args:
            vector_store: An optional VectorStore instance
        """
        self.vector_store = vector_store or VectorStore()
    
    def index_literary_works(self) -> None:
        """
        Index all literary works from the database.
        """
        # Load literary works from JSON file
        with open("app/database/literary_works.json", "r") as f:
            literary_works = json.load(f)
        
        texts = []
        metadata = []
        
        for work in literary_works:
            # Read the text file
            with open(work["path"], "r", encoding="utf-8") as f:
                text = f.read()
            
            texts.append(text)
            metadata.append({
                "title": work["title"],
                "author": work["author"],
                "path": work["path"]
            })
        
        # Add texts to vector store
        self.vector_store.add_texts(texts, metadata)
    
    def get_relevant_excerpts(self, query: str, litwork_id: int, k: int = 5) -> str:
        """
        Get relevant excerpts from a literary work based on a query.
        
        Args:
            query: The query text
            litwork_id: The ID of the literary work
            k: The number of excerpts to return
            
        Returns:
            A string containing the relevant excerpts
        """
        # Get the literary work
        litwork = get_litwork_by_id(litwork_id)
        if not litwork:
            return ""
        
        # Search for relevant excerpts
        results = self.vector_store.similarity_search(query, k=k)
        
        # Filter results to only include excerpts from the specified literary work
        filtered_results = [
            result for result in results 
            if result["metadata"].get("path") == litwork.path
        ]
        
        # Combine excerpts
        excerpts = "\n\n".join([result["text"] for result in filtered_results])
        
        return excerpts
    
    def get_relevant_excerpts_for_questionary(self, litwork_id: int, k: int = 5) -> str:
        """
        Get relevant excerpts for generating a questionary.
        
        Args:
            litwork_id: The ID of the literary work
            k: The number of excerpts to return
            
        Returns:
            A string containing the relevant excerpts
        """
        # Use a generic query to get diverse excerpts
        query = "main themes characters plot important events"
        return self.get_relevant_excerpts(query, litwork_id, k)
    
    def get_relevant_excerpts_for_discussion(self, query: str, litwork_id: int, k: int = 5) -> str:
        """
        Get relevant excerpts for a discussion.
        
        Args:
            query: The user's query
            litwork_id: The ID of the literary work
            k: The number of excerpts to return
            
        Returns:
            A string containing the relevant excerpts
        """
        return self.get_relevant_excerpts(query, litwork_id, k)
    
    def get_relevant_excerpts_for_idea(self, topic: str, litwork_id: int, k: int = 5) -> str:
        """
        Get relevant excerpts for generating an idea.
        
        Args:
            topic: The topic to generate an idea for
            litwork_id: The ID of the literary work
            k: The number of excerpts to return
            
        Returns:
            A string containing the relevant excerpts
        """
        return self.get_relevant_excerpts(topic, litwork_id, k) 