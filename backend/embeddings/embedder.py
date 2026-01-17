"""
Embeddings Module for NeuroDrive
Author: Pavan (Member 3) - Improved by Shashwat (Team Lead)
Purpose: Convert text into vector embeddings using Sentence Transformers
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


class Embedder:
    """
    Handles text-to-vector conversion using Sentence Transformers
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder with a pre-trained model
        
        Args:
            model_name: Name of the sentence transformer model
        """
        print(f"[LOADING] Loading embedding model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"[OK] Model loaded! Embedding dimension: {self.dimension}")
        except Exception as e:
            print(f"[ERROR] Error loading model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], show_progress: bool = False) -> np.ndarray:
        """
        Convert text(s) into vector embeddings
        
        Args:
            texts: Single text string or list of text strings
            show_progress: Show progress bar for batch encoding
            
        Returns:
            numpy array of embeddings (single vector or matrix)
        """
        try:
            # Handle single text
            if isinstance(texts, str):
                embedding = self.model.encode(texts, show_progress_bar=False)
                return np.array(embedding, dtype=np.float32)
            
            # Handle list of texts
            embeddings = self.model.encode(
                texts, 
                show_progress_bar=show_progress,
                batch_size=32
            )
            return np.array(embeddings, dtype=np.float32)
            
        except Exception as e:
            print(f"[ERROR] Error encoding text: {e}")
            raise
    
    def get_dimension(self) -> int:
        """
        Get the embedding dimension size
        
        Returns:
            Dimension of embedding vectors
        """
        return self.dimension
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode texts in batches (useful for large datasets)
        
        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once
            
        Returns:
            numpy array of embeddings
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True
            )
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            print(f"[ERROR] Error in batch encoding: {e}")
            raise


# Test the embedder
if __name__ == "__main__":
    print(" Testing Embedder Module...\n")
    
    # Initialize embedder
    embedder = Embedder()
    
    # Test 1: Single text
    print("Test 1: Single text encoding")
    text = "This is a sample document about machine learning."
    embedding = embedder.encode(text)
    print(f"[OK] Text: '{text[:50]}...'")
    print(f"[OK] Embedding shape: {embedding.shape}")
    print(f"[OK] First 5 values: {embedding[:5]}\n")
    
    # Test 2: Multiple texts
    print("Test 2: Batch encoding")
    texts = [
        "Machine learning is a subset of artificial intelligence.",
        "Python is a popular programming language.",
        "Data science involves statistics and programming."
    ]
    embeddings = embedder.encode(texts, show_progress=True)
    print(f"[OK] Encoded {len(texts)} texts")
    print(f"[OK] Embeddings shape: {embeddings.shape}")
    print(f"[OK] Dimension: {embedder.get_dimension()}\n")
    
    print(" Embedder module test complete!")

