# RAG System for Literary Works

This module implements a Retrieval-Augmented Generation (RAG) system for the StudyMate bot. The RAG system allows the bot to efficiently retrieve relevant excerpts from literary works based on user queries, rather than loading the entire text file into memory.

## Components

- **VectorStore**: A class that handles vector embeddings and similarity search using FAISS.
- **RAGManager**: A manager class that provides high-level operations for the RAG system.
- **initialize_rag.py**: A script to initialize the RAG system by indexing all literary works.

## How It Works

1. **Indexing**: When the bot starts up, it indexes all literary works by:
   - Splitting each text into overlapping chunks
   - Generating embeddings for each chunk using a sentence transformer model
   - Storing the embeddings in a FAISS index

2. **Retrieval**: When a user makes a query (e.g., asks a question about a literary work), the system:
   - Generates an embedding for the query
   - Searches for the most similar chunks in the index
   - Returns the top 5 most relevant chunks

3. **Generation**: The retrieved chunks are then used to augment the prompt sent to the LLM, allowing it to generate more relevant and accurate responses.

## Benefits

- **Efficiency**: Only the most relevant excerpts are included in the prompt, reducing token usage and cost.
- **Relevance**: Responses are more focused on the specific aspects of the literary work that are relevant to the user's query.
- **Scalability**: The system can handle large literary works without loading the entire text into memory.

## Usage

The RAG system is automatically initialized when the bot starts up. No additional configuration is required.

To manually initialize the RAG system, run:

```bash
python -m app.rag.initialize_rag
``` 