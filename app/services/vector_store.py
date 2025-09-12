"""
Vector store for document similarity search and retrieval
"""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from pinecone import Pinecone
from loguru import logger

from app.core.config import settings


class VectorStore:
    """Vector store for document similarity search"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.pinecone_index = None
        self.collection_name = "ai_assistant_documents"
        self.is_ready = False
    
    async def initialize(self):
        """Initialize vector store"""
        try:
            logger.info("Initializing Vector Store...")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB (local vector database)
            await self._init_chromadb()
            
            # Initialize Pinecone if available
            if settings.PINECONE_API_KEY:
                await self._init_pinecone()
            
            self.is_ready = True
            logger.success("Vector Store initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vector Store: {e}")
            raise
    
    async def _init_chromadb(self):
        """Initialize ChromaDB"""
        try:
            # Create ChromaDB client with new configuration
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db"
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(self.collection_name)
                logger.info("Using existing ChromaDB collection")
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AI Assistant document embeddings"}
                )
                logger.info("Created new ChromaDB collection")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def _init_pinecone(self):
        """Initialize Pinecone (optional)"""
        try:
            # Initialize Pinecone client
            pinecone = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Check if index exists
            index_name = "ai-assistant-docs"
            indexes = pinecone.list_indexes()
            if not any(index.name == index_name for index in indexes):
                # Create index
                pinecone.create_index(
                    name=index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric="cosine"
                )
                logger.info("Created Pinecone index")
            
            self.pinecone_index = pinecone.Index(index_name)
            logger.info("Pinecone initialized successfully")
            
        except Exception as e:
            logger.warning(f"Pinecone initialization failed: {e}")
            self.pinecone_index = None
    
    async def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add document to vector store"""
        try:
            # Generate embeddings
            embedding = self.embedding_model.encode(content).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}]
            )
            
            # Add to Pinecone if available
            if self.pinecone_index:
                self.pinecone_index.upsert(
                    vectors=[(doc_id, embedding, metadata or {})]
                )
            
            logger.debug(f"Added document {doc_id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            return False
    
    async def search_similar(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            similar_docs = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    if similarity >= threshold:
                        similar_docs.append({
                            'id': results['ids'][0][i],
                            'content': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                            'similarity': similarity
                        })
            
            logger.debug(f"Found {len(similar_docs)} similar documents for query: {query[:50]}...")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store"""
        try:
            # Delete from ChromaDB
            self.collection.delete(ids=[doc_id])
            
            # Delete from Pinecone if available
            if self.pinecone_index:
                self.pinecone_index.delete(ids=[doc_id])
            
            logger.debug(f"Deleted document {doc_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {e}")
            return False
    
    async def update_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update document in vector store"""
        try:
            # Delete old version
            await self.delete_document(doc_id)
            
            # Add new version
            return await self.add_document(doc_id, content, metadata)
            
        except Exception as e:
            logger.error(f"Error updating document in vector store: {e}")
            return False
    
    async def get_document_count(self) -> int:
        """Get total number of documents"""
        try:
            # Get count from ChromaDB
            results = self.collection.get()
            return len(results['ids']) if results['ids'] else 0
            
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    async def cleanup(self):
        """Cleanup vector store resources"""
        try:
            if self.chroma_client:
                # Persist ChromaDB
                self.chroma_client.persist()
            
            self.is_ready = False
            logger.info("Vector Store cleaned up")
            
        except Exception as e:
            logger.error(f"Error during vector store cleanup: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check vector store health"""
        try:
            doc_count = await self.get_document_count()
            
            return {
                "status": "healthy" if self.is_ready else "unhealthy",
                "chromadb": bool(self.chroma_client),
                "pinecone": bool(self.pinecone_index),
                "embedding_model": bool(self.embedding_model),
                "document_count": doc_count
            }
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
