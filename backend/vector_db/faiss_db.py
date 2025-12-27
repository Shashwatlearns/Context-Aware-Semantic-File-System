"""
FAISS Vector Database Module for NeuroDrive
Author: Pavan (Member 3) - Improved by Shashwat (Team Lead)
Purpose: Store and search vector embeddings with file metadata
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Optional, Tuple


class FAISSDatabase:
    """
    Manages FAISS vector database with file metadata
    """
    
    def __init__(self, dimension: int = 384, index_path: str = None):
        """
        Initialize FAISS database
        
        Args:
            dimension: Dimension of embedding vectors
            index_path: Path to save/load FAISS index
        """
        self.dimension = dimension
        self.index_path = index_path or "./data/indexes/faiss_index.bin"
        self.metadata_path = self.index_path.replace('.bin', '_metadata.pkl')
        
        # Initialize index
        self.index = None
        self.metadata = []  # Store file information
        
        # Try to load existing index, otherwise create new
        if os.path.exists(self.index_path):
            self.load()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        print(f"🔧 Creating new FAISS index (dimension: {self.dimension})...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("✅ New index created")
    
    def add(self, embeddings: np.ndarray, file_info: Dict):
        """
        Add embeddings with metadata to the database
        
        Args:
            embeddings: Vector embeddings (can be single or batch)
            file_info: Dictionary with file metadata
                      Required keys: 'path', 'name', 'text'
                      Optional: 'ext', 'size', 'created', 'modified'
        """
        try:
            # Ensure embeddings are 2D
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)
            
            # Convert to float32
            embeddings = embeddings.astype(np.float32)
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store metadata
            self.metadata.append(file_info)
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding to database: {e}")
            return False
    
    def add_batch(self, embeddings: np.ndarray, file_infos: List[Dict]):
        """
        Add multiple embeddings at once
        
        Args:
            embeddings: Matrix of embeddings (n_samples x dimension)
            file_infos: List of file metadata dictionaries
        """
        try:
            if len(embeddings) != len(file_infos):
                raise ValueError("Number of embeddings must match number of file_infos")
            
            # Convert to float32
            embeddings = embeddings.astype(np.float32)
            
            # Add to index
            self.index.add(embeddings)
            
            # Store metadata
            self.metadata.extend(file_infos)
            
            print(f"✅ Added {len(embeddings)} vectors to database")
            return True
            
        except Exception as e:
            print(f"❌ Error in batch add: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            
        Returns:
            List of dictionaries with file info and similarity scores
        """
        try:
            if self.index.ntotal == 0:
                print("⚠️  Database is empty")
                return []
            
            # Ensure query is 2D
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Convert to float32
            query_embedding = query_embedding.astype(np.float32)
            
            # Limit k to available vectors
            k = min(k, self.index.ntotal)
            
            # Search
            distances, indices = self.index.search(query_embedding, k)
            
            # Prepare results
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['distance'] = float(dist)
                    result['similarity_score'] = float(1 / (1 + dist))  # Convert distance to similarity
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    def save(self, index_path: str = None, metadata_path: str = None):
        """
        Save FAISS index and metadata to disk
        
        Args:
            index_path: Path to save index (optional)
            metadata_path: Path to save metadata (optional)
        """
        try:
            # Use default paths if not provided
            index_path = index_path or self.index_path
            metadata_path = metadata_path or self.metadata_path
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            print(f"✅ Database saved to {index_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving database: {e}")
            return False
    
    def load(self, index_path: str = None, metadata_path: str = None):
        """
        Load FAISS index and metadata from disk
        
        Args:
            index_path: Path to index file (optional)
            metadata_path: Path to metadata file (optional)
        """
        try:
            # Use default paths if not provided
            index_path = index_path or self.index_path
            metadata_path = metadata_path or self.metadata_path
            
            if not os.path.exists(index_path):
                print(f"⚠️  Index file not found: {index_path}")
                self._create_new_index()
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                self.metadata = []
            
            print(f"✅ Loaded database with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            self._create_new_index()
            return False
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'metadata_count': len(self.metadata),
            'index_path': self.index_path
        }
    
    def clear(self):
        """Clear all data from database"""
        self._create_new_index()
        print("✅ Database cleared")


# Test the database
if __name__ == "__main__":
    print("🔍 Testing FAISS Database...\n")
    
    # Test 1: Create database
    print("Test 1: Creating database")
    db = FAISSDatabase(dimension=384)
    print(f"Stats: {db.get_stats()}\n")
    
    # Test 2: Add some test vectors
    print("Test 2: Adding vectors")
    test_vectors = np.random.rand(5, 384).astype(np.float32)
    test_files = [
        {'path': f'/path/to/file{i}.pdf', 'name': f'file{i}.pdf', 'text': f'Sample text {i}'}
        for i in range(5)
    ]
    
    for vec, info in zip(test_vectors, test_files):
        db.add(vec, info)
    
    print(f"✅ Added {len(test_files)} vectors")
    print(f"Stats: {db.get_stats()}\n")
    
    # Test 3: Search
    print("Test 3: Searching")
    query = np.random.rand(384).astype(np.float32)
    results = db.search(query, k=3)
    
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"  - {r['name']} (score: {r['similarity_score']:.4f})")
    print()
    
    # Test 4: Save and load
    print("Test 4: Save and load")
    db.save()
    
    db2 = FAISSDatabase(dimension=384)
    print(f"Loaded stats: {db2.get_stats()}")
    
    print("\n🎉 FAISS Database test complete!")