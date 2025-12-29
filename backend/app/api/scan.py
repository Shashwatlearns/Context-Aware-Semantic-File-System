from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from file_scanner.scanner import scan_directory
from extraction.extraction_module import extract_content
from embeddings.embedder import Embedder
from vector_db.faiss_db import FAISSDatabase

router = APIRouter()

# Initialize embedder and database (singleton pattern)
embedder = None
db = None

class ScanRequest(BaseModel):
    folder_path: str

@router.post('/')
def scan_and_index(request: ScanRequest):
    '''Scan folder, extract text, create embeddings, and store in FAISS'''
    global embedder, db
    
    try:
        # Initialize if needed
        if embedder is None:
            embedder = Embedder()
        if db is None:
            db = FAISSDatabase(dimension=embedder.get_dimension())
        
        # Step 1: Scan directory
        files = scan_directory(request.folder_path)
        if isinstance(files, dict) and 'error' in files:
            raise HTTPException(status_code=400, detail=files['error'])
        
        # Step 2: Filter supported files
        supported_exts = {'.pdf', '.docx', '.txt'}
        supported_files = [f for f in files if f.get('ext') in supported_exts]
        
        if not supported_files:
            return {'message': 'No supported files found', 'files_indexed': 0}
        
        # Step 3: Extract and embed
        indexed_count = 0
        for file in supported_files:
            text = extract_content(file['path'], file['ext'])
            if text and not text.startswith('Error'):
                # Create embedding
                embedding = embedder.encode(text)
                
                # Store in database
                file_info = {
                    'path': file['path'],
                    'name': file['name'],
                    'ext': file['ext'],
                    'size': file.get('size', 0),
                    'text': text
                }
                db.add(embedding, file_info)
                indexed_count += 1
        
        # Save database
        db.save()
        
        return {
            'message': 'Indexing complete',
            'files_scanned': len(files),
            'files_indexed': indexed_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
