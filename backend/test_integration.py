"""
Complete Integration Test for NeuroDrive
Tests: File Scanner → Text Extraction → Embeddings → FAISS Storage → Search
Author: Shashwat (Team Lead)
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_scanner.scanner import scan_directory
from extraction.extraction_module import extract_content
from embeddings.embedder import Embedder
from vector_db.faiss_db import FAISSDatabase


def test_full_pipeline():
    """
    Complete integration test of all modules
    """
    print("="*70)
    print("🚀 NEURODRIVE - COMPLETE INTEGRATION TEST")
    print("="*70)
    print()
    
    # Configuration
    SAMPLE_FOLDER = os.path.join("..", "data", "sample_files")
    INDEX_PATH = os.path.join("..", "data", "indexes", "test_index.bin")
    
    # ========== STEP 1: SCAN FILES ==========
    print("📂 STEP 1: Scanning Directory")
    print("-" * 70)
    
    files = scan_directory(SAMPLE_FOLDER)
    
    if isinstance(files, dict) and "error" in files:
        print(f"❌ Error: {files['error']}")
        return
    
    print(f"✅ Found {len(files)} total files")
    
    # Filter supported files
    supported_exts = {".pdf", ".docx", ".txt"}
    supported_files = [f for f in files if f.get("ext") in supported_exts]
    
    print(f"✅ Found {len(supported_files)} supported files:")
    for f in supported_files:
        print(f"   - {f['name']} ({f['ext']})")
    print()
    
    if not supported_files:
        print("❌ No supported files found!")
        return
    
    # ========== STEP 2: EXTRACT TEXT ==========
    print("📝 STEP 2: Extracting Text from Files")
    print("-" * 70)
    
    file_data = []
    for f in supported_files:
        print(f"Processing: {f['name']}...", end=" ")
        text = extract_content(f["path"], f["ext"])
        
        if text and not text.startswith("Error"):
            file_data.append({
                "path": f["path"],
                "name": f["name"],
                "ext": f["ext"],
                "size": f.get("size", 0),
                "text": text,
                "char_count": len(text),
                "word_count": len(text.split())
            })
            print(f"✅ Extracted {len(text)} chars")
        else:
            print(f"❌ Failed")
    
    print(f"\n✅ Successfully extracted text from {len(file_data)} files")
    print()
    
    # ========== STEP 3: CREATE EMBEDDINGS ==========
    print("🧠 STEP 3: Creating Embeddings")
    print("-" * 70)
    
    embedder = Embedder()
    
    texts = [f["text"] for f in file_data]
    print(f"Encoding {len(texts)} documents...")
    
    embeddings = embedder.encode(texts, show_progress=True)
    
    print(f"✅ Created embeddings with shape: {embeddings.shape}")
    print(f"✅ Embedding dimension: {embedder.get_dimension()}")
    print()
    
    # ========== STEP 4: STORE IN FAISS ==========
    print("💾 STEP 4: Storing in FAISS Database")
    print("-" * 70)
    
    db = FAISSDatabase(dimension=embedder.get_dimension(), index_path=INDEX_PATH)
    
    # Add files one by one (with metadata)
    for embedding, file_info in zip(embeddings, file_data):
        db.add(embedding, file_info)
    
    stats = db.get_stats()
    print(f"✅ Database Statistics:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # Save database
    db.save()
    print("✅ Database saved to disk")
    print()
    
    # ========== STEP 5: TEST SEARCH ==========
    print("🔍 STEP 5: Testing Search Functionality")
    print("-" * 70)
    
    test_queries = [
        "machine learning and artificial intelligence",
        "data science and programming",
        "city and urban life"
    ]
    
    for query_text in test_queries:
        print(f"\n🔎 Query: '{query_text}'")
        print("-" * 50)
        
        # Encode query
        query_embedding = embedder.encode(query_text)
        
        # Search
        results = db.search(query_embedding, k=3)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n   {i}. {result['name']}")
                print(f"      Similarity Score: {result['similarity_score']:.4f}")
                print(f"      Path: {result['path']}")
                print(f"      Preview: {result['text'][:150]}...")
        else:
            print("❌ No results found")
    
    print()
    
    # ========== STEP 6: TEST PERSISTENCE ==========
    print("💿 STEP 6: Testing Database Persistence")
    print("-" * 70)
    
    print("Loading database from disk...")
    db2 = FAISSDatabase(dimension=embedder.get_dimension(), index_path=INDEX_PATH)
    
    stats2 = db2.get_stats()
    print(f"✅ Loaded database:")
    for key, value in stats2.items():
        print(f"   - {key}: {value}")
    
    # Test search with loaded database
    print("\nTesting search with loaded database...")
    query_embedding = embedder.encode("programming and technology")
    results = db2.search(query_embedding, k=2)
    
    print(f"✅ Found {len(results)} results from loaded database")
    print()
    
    # ========== FINAL SUMMARY ==========
    print("="*70)
    print("🎉 INTEGRATION TEST COMPLETE!")
    print("="*70)
    print("\n✅ All modules working together successfully!")
    print(f"\n📊 Summary:")
    print(f"   - Files Scanned: {len(files)}")
    print(f"   - Files Processed: {len(file_data)}")
    print(f"   - Embeddings Created: {len(embeddings)}")
    print(f"   - Vectors in Database: {stats['total_vectors']}")
    print(f"   - Search Queries Tested: {len(test_queries)}")
    print("\n🚀 System is ready for API integration!")


if __name__ == "__main__":
    try:
        test_full_pipeline()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()