import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from sentence_transformers import SentenceTransformer
import pickle
from pathlib import Path

class VectorStore:
    """
    A class to handle vector embeddings and similarity search for literary works.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = "data/vector_index"):
        """
        Initialize the vector store with a sentence transformer model.
        
        Args:
            model_name: The name of the sentence transformer model to use
            index_path: The path to save/load the vector index
        """
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.index = None
        self.texts = []
        self.metadata = []
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Load existing index if it exists
        if os.path.exists(f"{index_path}.index"):
            self.load_index()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to split
            chunk_size: The size of each chunk
            overlap: The overlap between chunks
            
        Returns:
            A list of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
        return chunks
    
    def add_texts(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of texts to add
            metadata: Optional metadata for each text
        """
        if metadata is None:
            metadata = [{} for _ in texts]
            
        # Process each text into chunks
        all_chunks = []
        all_metadata = []
        
        for text, meta in zip(texts, metadata):
            chunks = self.chunk_text(text)
            all_chunks.extend(chunks)
            all_metadata.extend([meta for _ in chunks])
        
        # Generate embeddings
        embeddings = self.model.encode(all_chunks, show_progress_bar=True)
        
        # Create or update FAISS index
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        # Add to index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store texts and metadata
        self.texts.extend(all_chunks)
        self.metadata.extend(all_metadata)
        
        # Save index
        self.save_index()
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar texts to the query.
        
        Args:
            query: The query text
            k: The number of results to return
            
        Returns:
            A list of dictionaries containing the text and metadata
        """
        if self.index is None or len(self.texts) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Search in index
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):  # Ensure index is valid
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadata[idx],
                    "distance": float(distances[0][i])
                })
        
        return results
    
    def save_index(self) -> None:
        """Save the index, texts, and metadata to disk."""
        if self.index is not None:
            faiss.write_index(self.index, f"{self.index_path}.index")
            
            with open(f"{self.index_path}.pkl", "wb") as f:
                pickle.dump({"texts": self.texts, "metadata": self.metadata}, f)
    
    def load_index(self) -> None:
        """Load the index, texts, and metadata from disk."""
        if os.path.exists(f"{self.index_path}.index"):
            self.index = faiss.read_index(f"{self.index_path}.index")
            
            with open(f"{self.index_path}.pkl", "rb") as f:
                data = pickle.load(f)
                self.texts = data["texts"]
                self.metadata = data["metadata"] 