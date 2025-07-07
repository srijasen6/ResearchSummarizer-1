import os
import pickle
import logging
import numpy as np
from typing import List, Dict, Any
from services.document_processor import DocumentProcessor

# Try to import AI libraries, fall back to None if not available
try:
    import faiss
except ImportError:
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class VectorStore:
    """Vector store for document similarity search"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Embedding model initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize embedding model: {e}")
        else:
            self.logger.warning("SentenceTransformer not available, using fallback search")
        
        self.document_processor = DocumentProcessor()
        self.indices = {}  # Document ID -> FAISS index
        self.chunks = {}   # Document ID -> List of chunks
        self.embeddings = {}  # Document ID -> embeddings
        
    def create_embeddings(self, document_id: int, text: str):
        """Create embeddings for a document"""
        try:
            # Clean and chunk the text
            clean_text = self.document_processor.clean_text(text)
            chunks = self.document_processor.chunk_text(clean_text)
            
            if not chunks:
                self.logger.warning(f"No chunks created for document {document_id}")
                return
            
            # Store chunks (with or without embeddings)
            self.chunks[document_id] = chunks
            
            if self.embedding_model and faiss:
                # Create embeddings for chunks
                chunk_texts = [chunk['text'] for chunk in chunks]
                embeddings = self.embedding_model.encode(chunk_texts)
                
                # Create FAISS index
                dimension = embeddings.shape[1]
                index = faiss.IndexFlatL2(dimension)
                index.add(embeddings.astype('float32'))
                
                # Store everything
                self.indices[document_id] = index
                self.embeddings[document_id] = embeddings
                
                # Save to disk
                self._save_to_disk(document_id)
                
                self.logger.info(f"Created embeddings for document {document_id} with {len(chunks)} chunks")
            else:
                self.logger.info(f"Stored {len(chunks)} chunks for document {document_id} (fallback mode)")
            
        except Exception as e:
            self.logger.error(f"Error creating embeddings for document {document_id}: {str(e)}")
            # Don't raise in fallback mode, just store chunks
            self.chunks[document_id] = chunks if 'chunks' in locals() else []
    
    def search_similar(self, document_id: int, query: str, k: int = 5) -> List[str]:
        """Search for similar chunks in the document"""
        try:
            # Load from disk if not in memory
            if document_id not in self.chunks and document_id not in self.indices:
                self._load_from_disk(document_id)
            
            chunks = self.chunks.get(document_id, [])
            if not chunks:
                self.logger.warning(f"No chunks found for document {document_id}")
                return []
            
            # If we have embeddings and FAISS, use semantic search
            if document_id in self.indices and self.embedding_model:
                try:
                    # Encode query
                    query_embedding = self.embedding_model.encode([query])
                    
                    # Search in FAISS index
                    index = self.indices[document_id]
                    
                    # Ensure k doesn't exceed number of chunks
                    k = min(k, len(chunks))
                    
                    distances, indices = index.search(query_embedding.astype('float32'), k)
                    
                    # Return the text of similar chunks
                    similar_chunks = []
                    for idx in indices[0]:
                        if idx < len(chunks):
                            similar_chunks.append(chunks[idx]['text'])
                    
                    return similar_chunks
                except Exception as e:
                    self.logger.warning(f"Semantic search failed, falling back to keyword search: {e}")
            
            # Fallback: simple keyword-based search
            return self._keyword_search(chunks, query, k)
            
        except Exception as e:
            self.logger.error(f"Error searching similar chunks for document {document_id}: {str(e)}")
            return []
    
    def _keyword_search(self, chunks: List[Dict], query: str, k: int = 5) -> List[str]:
        """Fallback keyword-based search"""
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for chunk in chunks:
            chunk_text = chunk['text'].lower()
            chunk_words = set(chunk_text.split())
            
            # Calculate simple word overlap score
            overlap = len(query_words.intersection(chunk_words))
            if overlap > 0:
                # Bonus for exact phrase matches
                if query.lower() in chunk_text:
                    overlap += 10
                scored_chunks.append((overlap, chunk['text']))
        
        # Sort by score (descending) and return top k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:k]]
    
    def get_document_chunks(self, document_id: int) -> List[Dict]:
        """Get all chunks for a document"""
        if document_id not in self.chunks:
            self._load_from_disk(document_id)
        
        return self.chunks.get(document_id, [])
    
    def _save_to_disk(self, document_id: int):
        """Save document embeddings to disk"""
        try:
            cache_dir = f"models_cache/doc_{document_id}"
            os.makedirs(cache_dir, exist_ok=True)
            
            # Save FAISS index if available
            if document_id in self.indices and faiss:
                faiss.write_index(self.indices[document_id], f"{cache_dir}/index.faiss")
            
            # Save chunks and embeddings
            with open(f"{cache_dir}/chunks.pkl", 'wb') as f:
                pickle.dump(self.chunks.get(document_id, []), f)
            
            with open(f"{cache_dir}/embeddings.pkl", 'wb') as f:
                pickle.dump(self.embeddings.get(document_id, []), f)
                
        except Exception as e:
            self.logger.error(f"Error saving to disk for document {document_id}: {str(e)}")
    
    def _load_from_disk(self, document_id: int):
        """Load document embeddings from disk"""
        try:
            cache_dir = f"models_cache/doc_{document_id}"
            
            if not os.path.exists(cache_dir):
                return
            
            # Load FAISS index if available
            index_path = f"{cache_dir}/index.faiss"
            if os.path.exists(index_path) and faiss:
                self.indices[document_id] = faiss.read_index(index_path)
            
            # Load chunks
            chunks_path = f"{cache_dir}/chunks.pkl"
            if os.path.exists(chunks_path):
                with open(chunks_path, 'rb') as f:
                    self.chunks[document_id] = pickle.load(f)
            
            # Load embeddings
            embeddings_path = f"{cache_dir}/embeddings.pkl"
            if os.path.exists(embeddings_path):
                with open(embeddings_path, 'rb') as f:
                    self.embeddings[document_id] = pickle.load(f)
                    
        except Exception as e:
            self.logger.error(f"Error loading from disk for document {document_id}: {str(e)}")
    
    def delete_document(self, document_id: int):
        """Delete document embeddings"""
        try:
            # Remove from memory
            if document_id in self.indices:
                del self.indices[document_id]
            if document_id in self.chunks:
                del self.chunks[document_id]
            if document_id in self.embeddings:
                del self.embeddings[document_id]
            
            # Remove from disk
            cache_dir = f"models_cache/doc_{document_id}"
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                
        except Exception as e:
            self.logger.error(f"Error deleting document {document_id}: {str(e)}")
