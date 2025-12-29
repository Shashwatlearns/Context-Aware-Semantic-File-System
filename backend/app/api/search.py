from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from embeddings.embedder import Embedder
from vector_db.faiss_db import FAISSDatabase

router = APIRouter()

embedder = None
db = None

class SearchRequest(BaseModel):
    query: str
    k: int = 5

@router.post('/')
def search(request: SearchRequest):
    '''Search for files using natural language query'''
    global embedder, db
    
    try:
        # Initialize if needed
        if embedder is None:
            embedder = Embedder()
        if db is None:
            db = FAISSDatabase(dimension=embedder.get_dimension())
        
        # Encode query
        query_embedding = embedder.encode(request.query)
        
        # Search
        results = db.search(query_embedding, k=request.k)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'name': result['name'],
                'path': result['path'],
                'similarity_score': result['similarity_score'],
                'preview': result['text'][:200] + '...'
            })
        
        return {
            'query': request.query,
            'results': formatted_results,
            'count': len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
