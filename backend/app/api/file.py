from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from vector_db.faiss_db import FAISSDatabase

router = APIRouter()

db = None

@router.get('/')
def get_all_files():
    '''Get list of all indexed files'''
    global db
    
    try:
        if db is None:
            db = FAISSDatabase(dimension=384)
        
        stats = db.get_stats()
        
        # Get all metadata
        files = []
        for metadata in db.metadata:
            files.append({
                'name': metadata['name'],
                'path': metadata['path'],
                'ext': metadata.get('ext', ''),
                'size': metadata.get('size', 0)
            })
        
        return {
            'files': files,
            'total': stats['total_vectors']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
